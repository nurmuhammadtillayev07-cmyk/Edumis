import os
import re
import shutil
import threading
import time
import urllib.request
import urllib.error
import json as json_lib
from functools import wraps
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from translations import translate

app = Flask(__name__)
# Muhim: production'da bu qiymatni muhit o'zgaruvchisidan (environment variable) oling
app.secret_key = os.environ.get('EDUMIS_SECRET_KEY', 'dev-key-change-me')
DB_NAME = "edumis.db"


def t(key):
    """Shablonlar ichida {{ t('kalit') }} shaklida chaqiriladigan tarjima funksiyasi."""
    lang = session.get('language', 'uz')
    return translate(key, lang)


app.jinja_env.globals['t'] = t

# ---------- Zaxira nusxalash (Backup) sozlamalari ----------
BACKUP_DIR = "backups"
BACKUP_INTERVAL_HOURS = 24   # avtomatik zaxira har necha soatda olinadi
MAX_BACKUPS = 14             # eng ko'p saqlanadigan zaxira soni (eskilari o'chiriladi)
BACKUP_NAME_RE = re.compile(r'^edumis_backup_\d{8}_\d{6}\.db$')


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def create_backup():
    """edumis.db faylining zaxira nusxasini backups/ papkasiga oladi va eskilarini tozalaydi."""
    if not os.path.exists(DB_NAME):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'edumis_backup_{timestamp}.db')
    shutil.copy2(DB_NAME, backup_path)

    existing = sorted(
        f for f in os.listdir(BACKUP_DIR)
        if BACKUP_NAME_RE.match(f)
    )
    while len(existing) > MAX_BACKUPS:
        oldest = existing.pop(0)
        try:
            os.remove(os.path.join(BACKUP_DIR, oldest))
        except OSError:
            pass
    return backup_path


def auto_backup_loop():
    """Fon rejimida ishlaydigan tsikl - belgilangan intervalda avtomatik zaxira oladi."""
    while True:
        time.sleep(BACKUP_INTERVAL_HOURS * 3600)
        try:
            create_backup()
        except Exception as e:
            print("Avtomatik zaxira olishda xatolik:", e)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        gender TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        class_id TEXT,
        birth_date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    # UNIQUE(student_id, date) - bir kunda bitta o'quvchiga bitta davomat yozuvi
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        UNIQUE(student_id, date),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT,
        phone TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS classrooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_no TEXT NOT NULL,
        capacity INTEGER,
        type TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id TEXT,
        subject_name TEXT,
        lesson_time TEXT,
        room_number TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS quarterly_grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, final INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        date TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ai_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS login_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        ip_address TEXT,
        device TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    # Migratsiya: eski bazalarga yangi ustunlarni qo'shish (mavjud bo'lsa xato e'tiborsiz qoldiriladi)
    new_columns = [
        ('phone', "TEXT"),
        ('email', "TEXT"),
        ('position', "TEXT"),
        ('theme', "TEXT DEFAULT 'light'"),
        ('language', "TEXT DEFAULT 'uz'"),
        ('notify_grades', "INTEGER DEFAULT 1"),
        ('notify_attendance', "INTEGER DEFAULT 1"),
        ('notify_homework', "INTEGER DEFAULT 1"),
    ]
    for col_name, col_def in new_columns:
        try:
            cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_def}')
        except sqlite3.OperationalError:
            pass  # ustun allaqachon mavjud
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'admin', 'Tizim Administratori')
        )
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = get_db_connection()
    row = conn.execute('SELECT value FROM app_settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO app_settings (key, value) VALUES (?, ?) '
        'ON CONFLICT(key) DO UPDATE SET value = excluded.value',
        (key, value)
    )
    conn.commit()
    conn.close()


# ---------- SI (Claude API) yordamida hisobot ----------

ANTHROPIC_MODEL = "claude-sonnet-5"


def get_anthropic_api_key():
    # Avval bazadagi sozlamadan, topilmasa muhit o'zgaruvchisidan olinadi
    return get_setting('anthropic_api_key') or os.environ.get('ANTHROPIC_API_KEY', '')


def call_claude(prompt, max_tokens=800):
    api_key = get_anthropic_api_key()
    if not api_key:
        return None, "Anthropic API kaliti sozlanmagan. Sozlamalar bo'limidan kiriting."

    body = json_lib.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json_lib.loads(resp.read().decode('utf-8'))
            text_parts = [b['text'] for b in data.get('content', []) if b.get('type') == 'text']
            return "\n".join(text_parts).strip(), None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        try:
            err_json = json_lib.loads(err_body)
            err_msg = err_json.get('error', {}).get('message', err_body)
        except ValueError:
            err_msg = err_body
        return None, f"API xatosi ({e.code}): {err_msg[:200]}"
    except urllib.error.URLError as e:
        return None, f"Internetga ulanib bo'lmadi: {e.reason}"
    except Exception as e:
        return None, f"Kutilmagan xatolik: {e}"


def gather_report_stats():
    conn = get_db_connection()
    students_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_marks = conn.execute('SELECT COUNT(*) FROM attendance').fetchone()[0]
    present_marks = conn.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Keldi'").fetchone()[0]
    attendance_rate = round((present_marks / total_marks) * 100, 1) if total_marks else 0

    low_attendance = conn.execute(
        "SELECT u.full_name, s.class_id, "
        "SUM(CASE WHEN a.status = 'Keldi' THEN 1 ELSE 0 END) * 1.0 / COUNT(a.id) as rate, "
        "COUNT(a.id) as total "
        "FROM students s JOIN users u ON s.user_id = u.id "
        "JOIN attendance a ON a.student_id = s.id "
        "GROUP BY s.id HAVING total >= 1 ORDER BY rate ASC LIMIT 5"
    ).fetchall()

    grade_avg = conn.execute(
        "SELECT subject, AVG(final) as avg_grade, COUNT(*) as cnt "
        "FROM quarterly_grades WHERE final IS NOT NULL "
        "GROUP BY subject ORDER BY avg_grade ASC"
    ).fetchall()

    class_counts = conn.execute(
        'SELECT class_id, COUNT(*) as cnt FROM students '
        'WHERE class_id IS NOT NULL AND class_id != "" '
        'GROUP BY class_id'
    ).fetchall()
    conn.close()

    return {
        'students_count': students_count,
        'attendance_rate': attendance_rate,
        'low_attendance': low_attendance,
        'grade_avg': grade_avg,
        'class_counts': class_counts,
    }


def build_report_prompt(stats):
    lines = [
        f"O'quvchilar soni: {stats['students_count']}",
        f"Umumiy davomat foizi: {stats['attendance_rate']}%",
    ]
    if stats['grade_avg']:
        lines.append("Fanlar bo'yicha o'rtacha yakuniy baho:")
        for g in stats['grade_avg']:
            lines.append(f"  - {g['subject']}: {round(g['avg_grade'], 2)} (namuna hajmi: {g['cnt']} ta baho)")
    if stats['low_attendance']:
        lines.append("Davomati eng past bo'lgan o'quvchilar:")
        for s in stats['low_attendance']:
            lines.append(f"  - {s['full_name']} ({s['class_id']}): {round(s['rate'] * 100, 1)}%")
    if stats['class_counts']:
        lines.append("Sinflar bo'yicha o'quvchilar soni:")
        for c in stats['class_counts']:
            lines.append(f"  - {c['class_id']}: {c['cnt']} ta")

    data_summary = "\n".join(lines)

    return (
        "Siz maktab ma'muriyati uchun ma'lumotlarni tahlil qiluvchi yordamchisiz. "
        "Quyidagi maktab statistikasi asosida qisqa, aniq va amaliy tavsiyalar beruvchi "
        "o'zbek tilida hisobot yozing.\n\n"
        f"MA'LUMOTLAR:\n{data_summary}\n\n"
        "Hisobot quyidagi qismlardan iborat bo'lsin:\n"
        "1. Umumiy holat (2-3 gap)\n"
        "2. Diqqat talab qiladigan joylar (agar bo'lsa)\n"
        "3. Aniq tavsiyalar (3-4 band)\n\n"
        "Hisobotni rasmiy, lekin tushunarli uslubda, markdown belgilarisiz oddiy matn "
        "ko'rinishida yozing. 200-250 so'z atrofida bo'lsin."
    )


# ---------- Ruxsatlarni tekshiruvchi decoratorlar ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash("Iltimos, avval tizimga kiring.", "error")
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash("Iltimos, avval tizimga kiring.", "error")
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash("Bu amal uchun sizda ruxsat yo'q.", "error")
                return redirect(url_for('dashboard'))
            return view(*args, **kwargs)
        return wrapped
    return decorator


# ---------- Marshrutlar ----------

@app.route('/')
def index():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))


@app.route('/sw.js')
def service_worker():
    """Service Worker - butun sayt uchun scope='/' bilan ildizdan xizmat qilinadi."""
    response = send_from_directory('static', 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/manifest.json')
def pwa_manifest():
    response = send_from_directory('static', 'manifest.json')
    response.headers['Content-Type'] = 'application/manifest+json'
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Login va parolni kiriting.", "error")
            return render_template('login.html')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        password_ok = False
        if user:
            try:
                password_ok = check_password_hash(user['password'], password)
            except (ValueError, TypeError):
                # Eski / hash qilinmagan parol formati - xavfsizlik uchun rad etamiz
                password_ok = False

        if user and password_ok:
            session.update({
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name'],
                'theme': user['theme'] or 'light',
                'language': user['language'] or 'uz',
            })
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO login_history (user_id, timestamp, ip_address, device) VALUES (?, ?, ?, ?)',
                (user['id'], datetime.now().strftime('%d.%m.%Y %H:%M'),
                 request.remote_addr, request.headers.get('User-Agent', '')[:120])
            )
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))

        flash("Login yoki parol noto'g'ri.", "error")
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') == 'student':
        return redirect(url_for('my_profile'))

    conn = get_db_connection()
    students_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    teachers_count = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'").fetchone()[0]
    classes_count = conn.execute('SELECT COUNT(DISTINCT class_id) FROM students').fetchone()[0]

    total_marks = conn.execute('SELECT COUNT(*) FROM attendance').fetchone()[0]
    present_marks = conn.execute("SELECT COUNT(*) FROM attendance WHERE status = 'Keldi'").fetchone()[0]
    attendance_rate = round((present_marks / total_marks) * 100, 1) if total_marks else 0

    # Oxirgi 14 kunlik davomat trendi (kunlik foiz)
    trend_rows = conn.execute(
        "SELECT date, "
        "SUM(CASE WHEN status = 'Keldi' THEN 1 ELSE 0 END) as present, "
        "COUNT(*) as total "
        "FROM attendance WHERE date >= date('now', '-13 days') "
        "GROUP BY date ORDER BY date"
    ).fetchall()
    trend_labels = [row['date'] for row in trend_rows]
    trend_values = [round((row['present'] / row['total']) * 100, 1) if row['total'] else 0 for row in trend_rows]

    # Sinflar bo'yicha o'quvchilar soni
    class_rows = conn.execute(
        'SELECT class_id, COUNT(*) as cnt FROM students '
        'WHERE class_id IS NOT NULL AND class_id != "" '
        'GROUP BY class_id ORDER BY class_id'
    ).fetchall()
    class_labels = [row['class_id'] for row in class_rows]
    class_values = [row['cnt'] for row in class_rows]

    conn.close()

    stats = {
        'students': students_count,
        'teachers': teachers_count,
        'classes': classes_count,
        'attendance_rate': attendance_rate,
    }
    chart_data = {
        'trend_labels': trend_labels,
        'trend_values': trend_values,
        'class_labels': class_labels,
        'class_values': class_values,
    }
    return render_template('dashboard.html', stats=stats, chart_data=chart_data)


@app.route('/mening-kabinetim')
@role_required('student')
def my_profile():
    conn = get_db_connection()
    student = conn.execute(
        'SELECT s.id, u.full_name, s.class_id, s.birth_date, u.gender, u.username as jshshir '
        'FROM students s JOIN users u ON s.user_id = u.id WHERE s.user_id = ?',
        (session['user_id'],)
    ).fetchone()

    if not student:
        conn.close()
        flash("O'quvchi profili topilmadi. Administrator bilan bog'laning.", "error")
        return redirect(url_for('login'))

    grades = conn.execute(
        'SELECT subject, q1, q2, q3, q4, final FROM quarterly_grades WHERE student_id = ? ORDER BY subject',
        (student['id'],)
    ).fetchall()

    attendance_records = conn.execute(
        'SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC',
        (student['id'],)
    ).fetchall()
    total = len(attendance_records)
    present = sum(1 for a in attendance_records if a['status'] == 'Keldi')
    attendance_rate = round((present / total) * 100, 1) if total else 0

    lessons = conn.execute(
        'SELECT lesson_time, subject_name, room_number, class_id FROM timetable '
        'WHERE class_id = ? ORDER BY lesson_time',
        (student['class_id'],)
    ).fetchall()
    conn.close()

    return render_template(
        'my_profile.html',
        student=student,
        grades=grades,
        attendance_records=attendance_records,
        attendance_rate=attendance_rate,
        lessons=lessons,
    )


@app.route('/students')
@role_required('admin')
def list_students():
    query = request.args.get('q', '').strip()
    selected_class = request.args.get('class_id', '').strip()

    conn = get_db_connection()
    sql = (
        'SELECT s.id, u.full_name, s.class_id, s.birth_date, u.username as jshshir '
        'FROM students s JOIN users u ON s.user_id = u.id WHERE 1=1'
    )
    params = []
    if query:
        sql += ' AND (u.full_name LIKE ? OR u.username LIKE ?)'
        params.extend([f'%{query}%', f'%{query}%'])
    if selected_class:
        sql += ' AND s.class_id = ?'
        params.append(selected_class)
    sql += ' ORDER BY u.full_name'

    students = conn.execute(sql, params).fetchall()
    all_classes = [
        row['class_id'] for row in
        conn.execute('SELECT DISTINCT class_id FROM students WHERE class_id IS NOT NULL ORDER BY class_id').fetchall()
    ]
    conn.close()
    return render_template(
        'students.html', students=students, query=query,
        selected_class=selected_class, all_classes=all_classes
    )


@app.route('/student/add', methods=['POST'])
@role_required('admin')
def add_student():
    jshshir = request.form.get('jshshir', '').strip()
    full_name = request.form.get('full_name', '').strip()
    gender = request.form.get('gender', '').strip()
    class_id = request.form.get('class_id', '').strip()
    birth_date = request.form.get('birth_date', '').strip()

    if not jshshir or not full_name:
        flash("JSHSHIR va F.I.Sh majburiy.", "error")
        return redirect(url_for('list_students'))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password, role, full_name, gender) VALUES (?, ?, ?, ?, ?)',
            (jshshir, generate_password_hash('student123'), 'student', full_name, gender)
        )
        cursor.execute(
            'INSERT INTO students (user_id, class_id, birth_date) VALUES (?, ?, ?)',
            (cursor.lastrowid, class_id, birth_date)
        )
        conn.commit()
        flash("O'quvchi muvaffaqiyatli qo'shildi.", "success")
    except sqlite3.IntegrityError:
        conn.rollback()
        flash("Bu JSHSHIR bilan foydalanuvchi allaqachon mavjud.", "error")
    except Exception:
        conn.rollback()
        flash("O'quvchini qo'shishda xatolik yuz berdi.", "error")
    finally:
        conn.close()
    return redirect(url_for('list_students'))


@app.route('/student/delete/<int:student_id>', methods=['POST'])
@role_required('admin')
def delete_student(student_id):
    conn = get_db_connection()
    student = conn.execute('SELECT user_id FROM students WHERE id = ?', (student_id,)).fetchone()
    if student:
        conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.execute('DELETE FROM users WHERE id = ?', (student['user_id'],))
        conn.commit()
        flash("O'quvchi o'chirildi.", "success")
    else:
        flash("O'quvchi topilmadi.", "error")
    conn.close()
    return redirect(url_for('list_students'))


@app.route('/student/<int:student_id>')
@role_required('admin')
def student_profile(student_id):
    conn = get_db_connection()
    row = conn.execute(
        'SELECT s.id, u.full_name, s.class_id, s.birth_date, u.gender, u.username as jshshir '
        'FROM students s JOIN users u ON s.user_id = u.id WHERE s.id = ?',
        (student_id,)
    ).fetchone()
    if not row:
        conn.close()
        return "Topilmadi", 404
    grades = conn.execute(
        'SELECT subject, q1, q2, q3, q4, final FROM quarterly_grades WHERE student_id = ?',
        (student_id,)
    ).fetchall()
    conn.close()
    student = dict(row)
    student['grades'] = grades
    return render_template('student_profile.html', student=student)


@app.route('/attendance', methods=['GET', 'POST'])
@role_required('admin')
def manage_attendance():
    conn = get_db_connection()
    if request.method == 'POST':
        selected_class = request.form.get('class_id', '').strip()
        today = datetime.now().strftime('%Y-%m-%d')
        for key, status in request.form.items():
            if key.startswith('status_'):
                student_id = key.split('_', 1)[1]
                # Bir kunda bir o'quvchi uchun bitta yozuv (dublikatning oldini olish)
                conn.execute(
                    'INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?) '
                    'ON CONFLICT(student_id, date) DO UPDATE SET status = excluded.status',
                    (student_id, today, status)
                )
        conn.commit()
        conn.close()
        flash("Davomat saqlandi.", "success")
        return redirect(url_for('manage_attendance', class_id=selected_class) if selected_class else url_for('manage_attendance'))

    selected_class = request.args.get('class_id', '').strip()
    sql = 'SELECT s.id, u.full_name, s.class_id FROM students s JOIN users u ON s.user_id = u.id'
    params = []
    if selected_class:
        sql += ' WHERE s.class_id = ?'
        params.append(selected_class)
    sql += ' ORDER BY u.full_name'
    students = conn.execute(sql, params).fetchall()
    all_classes = [
        row['class_id'] for row in
        conn.execute('SELECT DISTINCT class_id FROM students WHERE class_id IS NOT NULL ORDER BY class_id').fetchall()
    ]
    conn.close()
    return render_template(
        'attendance.html', students=students, datetime=datetime,
        selected_class=selected_class, all_classes=all_classes
    )


@app.route('/timetable')
@role_required('admin')
def view_timetable():
    conn = get_db_connection()
    lessons = conn.execute(
        'SELECT lesson_time, subject_name, room_number, class_id FROM timetable ORDER BY lesson_time'
    ).fetchall()
    conn.close()
    return render_template('timetable.html', lessons=lessons)


@app.route('/classrooms')
@role_required('admin')
def classrooms():
    conn = get_db_connection()
    rooms = conn.execute('SELECT room_no, capacity, type FROM classrooms ORDER BY room_no').fetchall()
    conn.close()
    return render_template('classrooms.html', rooms=rooms)


@app.route('/teachers')
@role_required('admin')
def teachers():
    conn = get_db_connection()
    t_list = conn.execute('SELECT name, subject, phone FROM teachers ORDER BY name').fetchall()
    conn.close()
    return render_template('teachers.html', teachers=t_list)


@app.route('/grades')
@role_required('admin')
def quarterly_grades():
    query = request.args.get('q', '').strip()
    conn = get_db_connection()
    sql = (
        'SELECT u.full_name as name, g.subject, g.q1, g.q2, g.q3, g.q4, g.final '
        'FROM quarterly_grades g '
        'JOIN students s ON g.student_id = s.id '
        'JOIN users u ON s.user_id = u.id '
    )
    params = []
    if query:
        sql += 'WHERE u.full_name LIKE ? OR g.subject LIKE ? '
        params.extend([f'%{query}%', f'%{query}%'])
    sql += 'ORDER BY u.full_name'
    grades_data = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template('grades.html', grades=grades_data, query=query)


@app.route('/notifications')
@login_required
def notifications():
    conn = get_db_connection()
    notifs = conn.execute('SELECT title, content, date FROM notifications ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('notifications.html', notifications=notifs)


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@app.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def settings_profile():
    conn = get_db_connection()
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        position = request.form.get('position', '').strip()

        if not full_name:
            flash("F.I.Sh bo'sh bo'lishi mumkin emas.", "error")
        else:
            conn.execute(
                'UPDATE users SET full_name = ?, phone = ?, email = ?, position = ? WHERE id = ?',
                (full_name, phone, email, position, session['user_id'])
            )
            conn.commit()
            session['full_name'] = full_name
            flash("Profil ma'lumotlari yangilandi.", "success")
        conn.close()
        return redirect(url_for('settings_profile'))

    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('settings_profile.html', user=user)


@app.route('/settings/appearance', methods=['GET', 'POST'])
@login_required
def settings_appearance():
    if request.method == 'POST':
        language = request.form.get('language', 'uz')
        theme = request.form.get('theme', 'light')
        session['language'] = language
        session['theme'] = theme
        conn = get_db_connection()
        conn.execute('UPDATE users SET theme = ?, language = ? WHERE id = ?', (theme, language, session['user_id']))
        conn.commit()
        conn.close()
        flash("Til va ko'rinish sozlamalari saqlandi.", "success")
        return redirect(url_for('settings_appearance'))

    current_theme = session.get('theme', 'light')
    current_language = session.get('language', 'uz')
    return render_template('settings_appearance.html', current_theme=current_theme, current_language=current_language)


@app.route('/settings/security', methods=['GET', 'POST'])
@login_required
def settings_security():
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        if len(new_password) < 6:
            flash("Parol kamida 6 ta belgidan iborat bo'lishi kerak.", "error")
        else:
            conn = get_db_connection()
            conn.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (generate_password_hash(new_password), session['user_id'])
            )
            conn.commit()
            conn.close()
            flash("Parol muvaffaqiyatli yangilandi.", "success")
        return redirect(url_for('settings_security'))

    conn = get_db_connection()
    history = conn.execute(
        'SELECT timestamp, ip_address, device FROM login_history '
        'WHERE user_id = ? ORDER BY id DESC LIMIT 10',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('settings_security.html', history=history)


@app.route('/settings/notifications', methods=['GET', 'POST'])
@login_required
def settings_notifications():
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute(
            'UPDATE users SET notify_grades = ?, notify_attendance = ?, notify_homework = ? WHERE id = ?',
            (
                1 if request.form.get('notify_grades') else 0,
                1 if request.form.get('notify_attendance') else 0,
                1 if request.form.get('notify_homework') else 0,
                session['user_id'],
            )
        )
        conn.commit()
        conn.close()
        flash("Bildirishnoma sozlamalari saqlandi.", "success")
        return redirect(url_for('settings_notifications'))

    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('settings_notifications.html', user=user)


@app.route('/settings/school', methods=['GET', 'POST'])
@role_required('admin')
def settings_school():
    if request.method == 'POST':
        set_setting('school_name', request.form.get('school_name', '').strip())
        set_setting('school_address', request.form.get('school_address', '').strip())
        set_setting('academic_year', request.form.get('academic_year', '').strip())
        set_setting('grading_system', request.form.get('grading_system', '5'))
        flash("Maktab sozlamalari saqlandi.", "success")
        return redirect(url_for('settings_school'))

    school_info = {
        'school_name': get_setting('school_name', ''),
        'school_address': get_setting('school_address', ''),
        'academic_year': get_setting('academic_year', ''),
        'grading_system': get_setting('grading_system', '5'),
    }
    return render_template('settings_school.html', school=school_info)


@app.route('/settings/data')
@role_required('admin')
def settings_data():
    return render_template('settings_data.html')


@app.route('/settings/about')
@login_required
def settings_about():
    return render_template('settings_about.html')


@app.route('/yordam/dars-jadvali')
@role_required('admin')
def help_timetable_guide():
    return render_template('help_timetable_guide.html')


# ---------- Excel (CSV) eksport marshrutlari ----------

def _csv_response(rows, header, filename):
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    output = buf.getvalue().encode('utf-8-sig')  # BOM - Excel'da o'zbek harflari to'g'ri chiqishi uchun
    from flask import Response
    return Response(
        output, mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.route('/export/students.csv')
@role_required('admin')
def export_students_csv():
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT u.full_name, u.username, s.class_id, s.birth_date, u.gender '
        'FROM students s JOIN users u ON s.user_id = u.id ORDER BY u.full_name'
    ).fetchall()
    conn.close()
    return _csv_response(
        [(r['full_name'], r['username'], r['class_id'], r['birth_date'], r['gender']) for r in rows],
        ['F.I.Sh', 'JSHSHIR', 'Sinf', "Tug'ilgan sana", 'Jinsi'],
        'oquvchilar.csv'
    )


@app.route('/export/grades.csv')
@role_required('admin')
def export_grades_csv():
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT u.full_name, g.subject, g.q1, g.q2, g.q3, g.q4, g.final '
        'FROM quarterly_grades g JOIN students s ON g.student_id = s.id '
        'JOIN users u ON s.user_id = u.id ORDER BY u.full_name'
    ).fetchall()
    conn.close()
    return _csv_response(
        [(r['full_name'], r['subject'], r['q1'], r['q2'], r['q3'], r['q4'], r['final']) for r in rows],
        ['F.I.Sh', 'Fan', '1-chorak', '2-chorak', '3-chorak', '4-chorak', 'Yakuniy'],
        'baholar.csv'
    )


@app.route('/export/attendance.csv')
@role_required('admin')
def export_attendance_csv():
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT u.full_name, s.class_id, a.date, a.status '
        'FROM attendance a JOIN students s ON a.student_id = s.id '
        'JOIN users u ON s.user_id = u.id ORDER BY a.date DESC'
    ).fetchall()
    conn.close()
    return _csv_response(
        [(r['full_name'], r['class_id'], r['date'], r['status']) for r in rows],
        ['F.I.Sh', 'Sinf', 'Sana', 'Holati'],
        'davomat.csv'
    )


# ---------- SI (Sun'iy Intellekt) hisobot marshrutlari ----------

@app.route('/ai-hisobot')
@role_required('admin')
def ai_report():
    conn = get_db_connection()
    reports = conn.execute(
        'SELECT id, content, created_at FROM ai_reports ORDER BY id DESC LIMIT 10'
    ).fetchall()
    conn.close()
    api_key = get_anthropic_api_key()
    masked_key = ('•' * 8 + api_key[-4:]) if api_key else ''
    return render_template('ai_report.html', reports=reports, api_configured=bool(api_key), masked_key=masked_key)


@app.route('/ai-hisobot/generate', methods=['POST'])
@role_required('admin')
def ai_report_generate():
    stats = gather_report_stats()
    prompt = build_report_prompt(stats)
    report_text, error = call_claude(prompt)

    if error:
        flash(f"Hisobot yaratib bo'lmadi: {error}", "error")
    else:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO ai_reports (content, created_at) VALUES (?, ?)',
            (report_text, datetime.now().strftime('%d.%m.%Y %H:%M'))
        )
        conn.commit()
        conn.close()
        flash("SI hisobot muvaffaqiyatli yaratildi.", "success")
    return redirect(url_for('ai_report'))


@app.route('/ai-hisobot/api-key', methods=['POST'])
@role_required('admin')
def ai_report_set_key():
    new_key = request.form.get('api_key', '').strip()
    if new_key:
        set_setting('anthropic_api_key', new_key)
        flash("API kalit saqlandi.", "success")
    else:
        flash("API kalit bo'sh bo'lishi mumkin emas.", "error")
    return redirect(url_for('ai_report'))


@app.route('/ai-hisobot/delete/<int:report_id>', methods=['POST'])
@role_required('admin')
def ai_report_delete(report_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM ai_reports WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()
    flash("Hisobot o'chirildi.", "success")
    return redirect(url_for('ai_report'))


# ---------- Zaxira nusxalash (Backup) marshrutlari ----------

def _safe_backup_filename(filename):
    """Yo'l aylanib o'tish (path traversal) hujumidan himoya - faqat ruxsat etilgan formatdagi nomni qaytaradi."""
    name = os.path.basename(filename)
    return name if BACKUP_NAME_RE.match(name) else None


@app.route('/backup')
@role_required('admin')
def backup_list():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    files = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if BACKUP_NAME_RE.match(f):
            path = os.path.join(BACKUP_DIR, f)
            files.append({
                'name': f,
                'size_kb': round(os.path.getsize(path) / 1024, 1),
                'time': datetime.fromtimestamp(os.path.getmtime(path)).strftime('%d.%m.%Y %H:%M'),
            })

    current_size_kb = round(os.path.getsize(DB_NAME) / 1024, 1) if os.path.exists(DB_NAME) else 0
    return render_template(
        'backup.html', backups=files, current_size_kb=current_size_kb,
        interval_hours=BACKUP_INTERVAL_HOURS, max_backups=MAX_BACKUPS
    )


@app.route('/backup/create', methods=['POST'])
@role_required('admin')
def backup_create():
    path = create_backup()
    if path:
        flash("Zaxira nusxa muvaffaqiyatli yaratildi.", "success")
    else:
        flash("Zaxira yaratib bo'lmadi - baza fayli topilmadi.", "error")
    return redirect(url_for('backup_list'))


@app.route('/backup/download/<path:filename>')
@role_required('admin')
def backup_download(filename):
    safe_name = _safe_backup_filename(filename)
    if not safe_name:
        flash("Noto'g'ri fayl nomi.", "error")
        return redirect(url_for('backup_list'))
    file_path = os.path.join(BACKUP_DIR, safe_name)
    if not os.path.exists(file_path):
        flash("Zaxira fayli topilmadi.", "error")
        return redirect(url_for('backup_list'))
    return send_file(file_path, as_attachment=True, download_name=safe_name)


@app.route('/backup/restore/<path:filename>', methods=['POST'])
@role_required('admin')
def backup_restore(filename):
    safe_name = _safe_backup_filename(filename)
    if not safe_name:
        flash("Noto'g'ri fayl nomi.", "error")
        return redirect(url_for('backup_list'))
    file_path = os.path.join(BACKUP_DIR, safe_name)
    if not os.path.exists(file_path):
        flash("Zaxira fayli topilmadi.", "error")
        return redirect(url_for('backup_list'))

    # Xavfsizlik uchun tiklashdan oldin joriy holatni ham zaxiralaymiz
    create_backup()
    shutil.copy2(file_path, DB_NAME)
    session.clear()
    flash("Baza tanlangan zaxiradan muvaffaqiyatli tiklandi. Qaytadan tizimga kiring.", "success")
    return redirect(url_for('login'))


@app.route('/backup/delete/<path:filename>', methods=['POST'])
@role_required('admin')
def backup_delete(filename):
    safe_name = _safe_backup_filename(filename)
    if safe_name:
        file_path = os.path.join(BACKUP_DIR, safe_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash("Zaxira nusxa o'chirildi.", "success")
    return redirect(url_for('backup_list'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Tizimdan chiqdingiz.", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    create_backup()  # dastur ishga tushganda darhol bitta zaxira olinadi
    threading.Thread(target=auto_backup_loop, daemon=True).start()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
else:
    # Gunicorn kabi WSGI server orqali ishga tushganda ham baza tayyor bo'lishi uchun
    init_db()
    create_backup()
    threading.Thread(target=auto_backup_loop, daemon=True).start()

import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from modules.timetable import register_timetable_module

app = Flask(__name__)
app.secret_key = "o'zgartiring-bu-maxfiy-kalitni-productionda"  # TODO: .env dan o'qing

DB_PATH = "edumis.db"


# ----------------------------------------------------------------------
# i18n stub — sizning asl loyihangizda to'liq tarjima tizimi (uz/ru/en)
# bor. Bu demo loyihada shablonlar buzilmasligi uchun oddiy stub:
# kalit topilmasa, o'zini qaytaradi. Asl loyihaga ulaganda buni
# haqiqiy translations lug'atingiz bilan almashtiring.
# ----------------------------------------------------------------------
@app.context_processor
def inject_translator():
    def t(key):
        return key
    return {"t": t}

# Tizimda mavjud bo'lgan yagona ruxsat etilgan rollar.
# Ro'yxatdan o'tish formasi HECH QACHON bu ro'yxatdan birini
# foydalanuvchiga tanlatmaydi — bu faqat ma'lumotlar bazasi darajasida
# nazorat qilinadigan tuxum.
VALID_ROLES = ("student", "teacher", "admin")


# ----------------------------------------------------------------------
# Ma'lumotlar bazasi
# ----------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
                CHECK (role IN ('student','teacher','admin'))
        )
    """)
    existing_admin = db.execute(
        "SELECT id FROM users WHERE role = 'admin'"
    ).fetchone()
    if not existing_admin:
        db.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            ("admin", generate_password_hash("Admin#12345")),
        )
    db.commit()
    db.close()


# ----------------------------------------------------------------------
# Ruxsat nazorati uchun yordamchi dekoratorlar
# ----------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Iltimos, avval tizimga kiring")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Iltimos, avval tizimga kiring")
                return redirect(url_for("login"))
            if session.get("role") not in allowed_roles:
                return "403 — Sizda bu sahifaga ruxsat yo'q", 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


# ----------------------------------------------------------------------
# Splash screen
# ----------------------------------------------------------------------
@app.route("/")
def splash():
    return render_template("splash.html")


# ----------------------------------------------------------------------
# Ro'yxatdan o'tish — MUAMMO SHU YERDA TUZATILDI:
# Forma faqat username/password oladi. "role" maydoni umuman
# formada yo'q va requestdan o'qilmaydi. Har bir yangi hisob
# serverda majburan role='student' bilan yaratiladi.
# ----------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Barcha maydonlarni to'ldiring")
            return redirect(url_for("register"))

        db = get_db()
        exists = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if exists:
            flash("Bu foydalanuvchi nomi band")
            return redirect(url_for("register"))

        # E'TIBOR: role qiymati hech qachon request.form dan olinmaydi.
        # request.form.get("role") kabi kod YOZILMAYDI — aks holda
        # foydalanuvchi POST so'rovini o'zgartirib (masalan DevTools yoki
        # curl orqali) role=admin yuborib, o'zini admin qilib olishi mumkin.
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'student')",
            (username, generate_password_hash(password)),
        )
        db.commit()
        flash("Ro'yxatdan o'tish muvaffaqiyatli. Endi tizimga kiring.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ----------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            # Rol ma'lumotlar bazasidan o'qiladi, foydalanuvchi
            # kiritgan hech qanday qiymatdan emas.
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))

        flash("Foydalanuvchi nomi yoki parol noto'g'ri")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return f"Xush kelibsiz, {session['username']} ({session['role']})"


# ----------------------------------------------------------------------
# Faqat ADMIN kira oladigan panel — mavjud foydalanuvchilarning
# rolini shu yerda, faqat admin sifatida tasdiqlangandan keyin
# o'zgartirish mumkin. Bu — rol o'zgartirishning YAGONA yo'li.
# ----------------------------------------------------------------------
@app.route("/admin/users")
@roles_required("admin")
def admin_users():
    db = get_db()
    users = db.execute("SELECT id, username, role FROM users").fetchall()
    rows = "".join(
        f"<tr><td>{u['id']}</td><td>{u['username']}</td><td>{u['role']}</td></tr>"
        for u in users
    )
    return f"<h3>Foydalanuvchilar</h3><table border='1'>{rows}</table>"


@app.route("/admin/users/<int:user_id>/set-role", methods=["POST"])
@roles_required("admin")
def set_role(user_id):
    new_role = request.form.get("role")
    if new_role not in VALID_ROLES:
        return "Noto'g'ri rol", 400
    db = get_db()
    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    db.commit()
    return redirect(url_for("admin_users"))


def seed_timetable_demo_data():
    """Faqat demo/test uchun — birinchi ishga tushirishda namuna
    sinf/o'qituvchi/fan/xona yozuvlarini qo'shadi. Productionda buni
    o'chirib, admin panel orqali haqiqiy ma'lumot kiritilsin."""
    db = sqlite3.connect(DB_PATH)
    if db.execute("SELECT COUNT(*) c FROM tt_classes").fetchone()[0] == 0:
        db.executemany("INSERT INTO tt_classes (name) VALUES (?)",
                        [("5-A",), ("6-B",), ("9-A",)])
        db.executemany("INSERT INTO tt_teachers (full_name) VALUES (?)",
                        [("Aliyeva Nodira",), ("Karimov Bekzod",), ("Yusupova Feruza",)])
        db.executemany("INSERT INTO tt_subjects (name, color) VALUES (?, ?)",
                        [("Matematika", "#2563eb"), ("Fizika", "#7c3aed"),
                         ("Ona tili", "#16a34a"), ("Tarix", "#f59e0b")])
        db.executemany("INSERT INTO tt_rooms (name) VALUES (?)",
                        [("101-xona",), ("102-xona",), ("Sport zali",)])
        db.commit()
    db.close()


register_timetable_module(app)

if __name__ == "__main__":
    init_db()
    seed_timetable_demo_data()
    app.run(host="0.0.0.0", port=5000, debug=True)

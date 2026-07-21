"""
EduMIS Haftalik Dars Jadvali — REST API.

Barcha endpointlar /api/timetable/... prefiksi ostida.
Ruxsatlar asosiy ilova (app.py)dagi session['role'] bilan ishlaydi:
  - student, teacher: faqat GET (o'qish)
  - admin: to'liq CRUD
"""
from functools import wraps
from flask import Blueprint, request, jsonify, session, send_file, g

from .db import get_db, close_db, WEEKDAYS, save_history
from .validators import check_conflicts
from .export_import import export_excel, export_pdf, import_excel
from . import realtime

api_bp = Blueprint("timetable_api", __name__, url_prefix="/api/timetable")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "Faqat admin uchun ruxsat etilgan"}), 403
        return view(*args, **kwargs)
    return wrapped


def login_required_api(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Tizimga kiring"}), 401
        return view(*args, **kwargs)
    return wrapped


@api_bp.teardown_request
def _teardown(exc):
    close_db(exc)


# ------------------------------------------------------------------
# Ma'lumotnomalar (reference data): sinflar, o'qituvchilar, fanlar, xonalar
# ------------------------------------------------------------------
@api_bp.get("/classes")
@login_required_api
def list_classes():
    db = get_db()
    rows = db.execute("SELECT * FROM tt_classes ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/teachers")
@login_required_api
def list_teachers():
    db = get_db()
    rows = db.execute("SELECT * FROM tt_teachers ORDER BY full_name").fetchall()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/subjects")
@login_required_api
def list_subjects():
    db = get_db()
    rows = db.execute("SELECT * FROM tt_subjects ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/rooms")
@login_required_api
def list_rooms():
    db = get_db()
    rows = db.execute("SELECT * FROM tt_rooms ORDER BY name").fetchall()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/slots")
@login_required_api
def list_slots():
    db = get_db()
    rows = db.execute("SELECT * FROM tt_slots ORDER BY slot_order").fetchall()
    return jsonify([dict(r) for r in rows])


# admin: fan/o'qituvchi/xona qo'shish (reference data boshqaruvi)
@api_bp.post("/subjects")
@admin_required
def create_subject():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    color = data.get("color") or "#2563eb"
    if not name:
        return jsonify({"error": "Fan nomi kerak"}), 400
    db = get_db()
    cur = db.execute("INSERT OR IGNORE INTO tt_subjects (name, color) VALUES (?, ?)", (name, color))
    db.commit()
    return jsonify({"ok": True, "id": cur.lastrowid})


@api_bp.delete("/subjects/<int:subject_id>")
@admin_required
def delete_subject(subject_id):
    db = get_db()
    in_use = db.execute("SELECT COUNT(*) c FROM tt_lessons WHERE subject_id = ?", (subject_id,)).fetchone()["c"]
    if in_use:
        return jsonify({"error": f"Bu fan {in_use} ta darsda ishlatilmoqda, avval ularni o'zgartiring"}), 409
    db.execute("DELETE FROM tt_subjects WHERE id = ?", (subject_id,))
    db.commit()
    return jsonify({"ok": True})


@api_bp.post("/slots/<int:slot_order>")
@admin_required
def update_slot_time(slot_order):
    """Dars vaqtini o'zgartirish."""
    data = request.get_json(force=True)
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    if not (start_time and end_time):
        return jsonify({"error": "start_time va end_time kerak"}), 400
    db = get_db()
    db.execute(
        "UPDATE tt_slots SET start_time = ?, end_time = ? WHERE slot_order = ?",
        (start_time, end_time, slot_order),
    )
    db.commit()
    realtime.broadcast("slots_changed", {"slot_order": slot_order})
    return jsonify({"ok": True})


# ------------------------------------------------------------------
# Bitta sinf uchun haftalik jadval (grid ko'rinishida)
# ------------------------------------------------------------------
def _serialize_class_grid(db, class_id):
    slots = db.execute("SELECT * FROM tt_slots ORDER BY slot_order").fetchall()
    lessons = db.execute(
        """
        SELECT l.*, s.name AS subject_name, s.color AS subject_color,
               t.full_name AS teacher_name, r.name AS room_name
        FROM tt_lessons l
        JOIN tt_subjects s ON s.id = l.subject_id
        JOIN tt_teachers t ON t.id = l.teacher_id
        JOIN tt_rooms r ON r.id = l.room_id
        WHERE l.class_id = ?
        """,
        (class_id,),
    ).fetchall()

    grid = {s["slot_order"]: {str(d): None for d, _ in WEEKDAYS} for s in slots}
    for l in lessons:
        grid[l["slot_order"]][str(l["day_of_week"])] = dict(l)

    return {
        "slots": [dict(s) for s in slots],
        "days": [{"num": d, "name": n} for d, n in WEEKDAYS],
        "grid": grid,
    }


@api_bp.get("/class/<int:class_id>")
@login_required_api
def get_class_timetable(class_id):
    db = get_db()
    return jsonify(_serialize_class_grid(db, class_id))


@api_bp.get("/teacher/<int:teacher_id>")
@login_required_api
def get_teacher_timetable(teacher_id):
    """O'qituvchining barcha sinflardagi darslari — haftalik grid ko'rinishida."""
    db = get_db()
    slots = db.execute("SELECT * FROM tt_slots ORDER BY slot_order").fetchall()
    lessons = db.execute(
        """
        SELECT l.*, s.name AS subject_name, s.color AS subject_color,
               c.name AS class_name, r.name AS room_name
        FROM tt_lessons l
        JOIN tt_subjects s ON s.id = l.subject_id
        JOIN tt_classes c ON c.id = l.class_id
        JOIN tt_rooms r ON r.id = l.room_id
        WHERE l.teacher_id = ?
        """,
        (teacher_id,),
    ).fetchall()

    grid = {s["slot_order"]: {str(d): None for d, _ in WEEKDAYS} for s in slots}
    for l in lessons:
        grid[l["slot_order"]][str(l["day_of_week"])] = dict(l)

    return jsonify({
        "slots": [dict(s) for s in slots],
        "days": [{"num": d, "name": n} for d, n in WEEKDAYS],
        "grid": grid,
    })


# ------------------------------------------------------------------
# Filtrlash va qidiruv
# ------------------------------------------------------------------
@api_bp.get("/search")
@login_required_api
def search():
    q = f"%{request.args.get('q', '').strip()}%"
    db = get_db()
    rows = db.execute(
        """
        SELECT l.id, c.name AS class_name, s.name AS subject_name,
               t.full_name AS teacher_name, r.name AS room_name,
               l.day_of_week, l.slot_order
        FROM tt_lessons l
        JOIN tt_classes c ON c.id = l.class_id
        JOIN tt_subjects s ON s.id = l.subject_id
        JOIN tt_teachers t ON t.id = l.teacher_id
        JOIN tt_rooms r ON r.id = l.room_id
        WHERE s.name LIKE ? OR t.full_name LIKE ? OR c.name LIKE ? OR r.name LIKE ?
        LIMIT 50
        """,
        (q, q, q, q),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@api_bp.get("/filter")
@login_required_api
def filter_lessons():
    """?class_id=&teacher_id=&subject_id=&room_id= — bir nechtasi birga ishlaydi."""
    db = get_db()
    clauses, params = [], []
    for field, param in [
        ("l.class_id", "class_id"),
        ("l.teacher_id", "teacher_id"),
        ("l.subject_id", "subject_id"),
        ("l.room_id", "room_id"),
    ]:
        val = request.args.get(param)
        if val:
            clauses.append(f"{field} = ?")
            params.append(val)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = db.execute(
        f"""
        SELECT l.*, c.name AS class_name, s.name AS subject_name,
               t.full_name AS teacher_name, r.name AS room_name
        FROM tt_lessons l
        JOIN tt_classes c ON c.id = l.class_id
        JOIN tt_subjects s ON s.id = l.subject_id
        JOIN tt_teachers t ON t.id = l.teacher_id
        JOIN tt_rooms r ON r.id = l.room_id
        {where}
        ORDER BY l.day_of_week, l.slot_order
        """,
        params,
    ).fetchall()
    return jsonify([dict(r) for r in rows])


# ------------------------------------------------------------------
# CRUD — dars qo'shish/tahrirlash (bitta katak, drag&drop shu orqali ishlaydi)
# ------------------------------------------------------------------
@api_bp.post("/lesson")
@admin_required
def upsert_lesson():
    """
    Body: {class_id, day_of_week, slot_order, subject_id, teacher_id, room_id, lesson_id?}
    lesson_id berilsa — mavjud katak yangilanadi (masalan drag&drop bilan
    ko'chirilganda), berilmasa — yangi dars yaratiladi.
    """
    data = request.get_json(force=True)
    required = ["class_id", "day_of_week", "slot_order", "subject_id", "teacher_id", "room_id"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "Barcha maydonlar kerak"}), 400

    db = get_db()
    conflicts = check_conflicts(
        db,
        class_id=data["class_id"],
        day_of_week=data["day_of_week"],
        slot_order=data["slot_order"],
        teacher_id=data["teacher_id"],
        room_id=data["room_id"],
        exclude_lesson_id=data.get("lesson_id"),
    )
    if conflicts:
        return jsonify({"error": "conflict", "conflicts": conflicts}), 409

    db.execute(
        """
        INSERT INTO tt_lessons (class_id, day_of_week, slot_order, subject_id, teacher_id, room_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(class_id, day_of_week, slot_order)
        DO UPDATE SET subject_id=excluded.subject_id, teacher_id=excluded.teacher_id,
                      room_id=excluded.room_id, updated_at=CURRENT_TIMESTAMP
        """,
        (data["class_id"], data["day_of_week"], data["slot_order"],
         data["subject_id"], data["teacher_id"], data["room_id"]),
    )
    save_history(db, data["class_id"], "Dars saqlandi", session.get("username", "admin"))
    db.commit()

    realtime.broadcast("lesson_changed", {"class_id": data["class_id"]})
    return jsonify({"ok": True})


@api_bp.delete("/lesson/<int:lesson_id>")
@admin_required
def delete_lesson(lesson_id):
    db = get_db()
    row = db.execute("SELECT class_id FROM tt_lessons WHERE id = ?", (lesson_id,)).fetchone()
    if not row:
        return jsonify({"error": "Topilmadi"}), 404
    db.execute("DELETE FROM tt_lessons WHERE id = ?", (lesson_id,))
    save_history(db, row["class_id"], "Dars o'chirildi", session.get("username", "admin"))
    db.commit()
    realtime.broadcast("lesson_changed", {"class_id": row["class_id"]})
    return jsonify({"ok": True})


@api_bp.post("/lesson/<int:lesson_id>/move")
@admin_required
def move_lesson(lesson_id):
    """Drag & Drop bilan darsni boshqa kun/slotga (yoki boshqa sinfga) ko'chirish."""
    data = request.get_json(force=True)
    db = get_db()
    lesson = db.execute("SELECT * FROM tt_lessons WHERE id = ?", (lesson_id,)).fetchone()
    if not lesson:
        return jsonify({"error": "Topilmadi"}), 404

    new_class_id = data.get("class_id", lesson["class_id"])
    new_day = data.get("day_of_week", lesson["day_of_week"])
    new_slot = data.get("slot_order", lesson["slot_order"])

    conflicts = check_conflicts(
        db, new_class_id, new_day, new_slot,
        lesson["teacher_id"], lesson["room_id"], exclude_lesson_id=lesson_id,
    )
    if conflicts:
        return jsonify({"error": "conflict", "conflicts": conflicts}), 409

    db.execute(
        "UPDATE tt_lessons SET class_id=?, day_of_week=?, slot_order=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (new_class_id, new_day, new_slot, lesson_id),
    )
    save_history(db, new_class_id, "Dars ko'chirildi (drag & drop)", session.get("username", "admin"))
    db.commit()
    realtime.broadcast("lesson_changed", {"class_id": new_class_id})
    return jsonify({"ok": True})


# ------------------------------------------------------------------
# Nusxalash: butun kunni yoki butun sinf jadvalini nusxalash
# ------------------------------------------------------------------
@api_bp.post("/copy-day")
@admin_required
def copy_day():
    """Body: {class_id, from_day, to_day}"""
    data = request.get_json(force=True)
    class_id, from_day, to_day = data["class_id"], data["from_day"], data["to_day"]
    db = get_db()

    source_lessons = db.execute(
        "SELECT * FROM tt_lessons WHERE class_id=? AND day_of_week=?",
        (class_id, from_day),
    ).fetchall()

    all_conflicts = []
    for l in source_lessons:
        conflicts = check_conflicts(
            db, class_id, to_day, l["slot_order"], l["teacher_id"], l["room_id"]
        )
        if conflicts:
            all_conflicts.append({"slot_order": l["slot_order"], "conflicts": conflicts})

    if all_conflicts:
        return jsonify({"error": "conflict", "details": all_conflicts}), 409

    for l in source_lessons:
        db.execute(
            """
            INSERT INTO tt_lessons (class_id, day_of_week, slot_order, subject_id, teacher_id, room_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(class_id, day_of_week, slot_order)
            DO UPDATE SET subject_id=excluded.subject_id, teacher_id=excluded.teacher_id,
                          room_id=excluded.room_id, updated_at=CURRENT_TIMESTAMP
            """,
            (class_id, to_day, l["slot_order"], l["subject_id"], l["teacher_id"], l["room_id"]),
        )
    save_history(db, class_id, f"Kun nusxalandi ({from_day} -> {to_day})", session.get("username", "admin"))
    db.commit()
    realtime.broadcast("lesson_changed", {"class_id": class_id})
    return jsonify({"ok": True, "copied": len(source_lessons)})


@api_bp.post("/copy-class")
@admin_required
def copy_class():
    """Body: {source_class_id, target_class_id}. Maqsad sinfdagi mavjud jadval ustidan yoziladi."""
    data = request.get_json(force=True)
    source_id, target_id = data["source_class_id"], data["target_class_id"]
    db = get_db()

    source_lessons = db.execute(
        "SELECT * FROM tt_lessons WHERE class_id=?", (source_id,)
    ).fetchall()

    all_conflicts = []
    for l in source_lessons:
        conflicts = check_conflicts(
            db, target_id, l["day_of_week"], l["slot_order"], l["teacher_id"], l["room_id"]
        )
        if conflicts:
            all_conflicts.append({
                "day": l["day_of_week"], "slot_order": l["slot_order"], "conflicts": conflicts
            })

    if all_conflicts:
        return jsonify({"error": "conflict", "details": all_conflicts}), 409

    for l in source_lessons:
        db.execute(
            """
            INSERT INTO tt_lessons (class_id, day_of_week, slot_order, subject_id, teacher_id, room_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(class_id, day_of_week, slot_order)
            DO UPDATE SET subject_id=excluded.subject_id, teacher_id=excluded.teacher_id,
                          room_id=excluded.room_id, updated_at=CURRENT_TIMESTAMP
            """,
            (target_id, l["day_of_week"], l["slot_order"], l["subject_id"], l["teacher_id"], l["room_id"]),
        )
    save_history(db, target_id, f"Boshqa sinfdan nusxalandi (sinf #{source_id})", session.get("username", "admin"))
    db.commit()
    realtime.broadcast("lesson_changed", {"class_id": target_id})
    return jsonify({"ok": True, "copied": len(source_lessons)})


# ------------------------------------------------------------------
# Version history — ko'rish va eski holatga qaytarish
# ------------------------------------------------------------------
@api_bp.get("/history/<int:class_id>")
@admin_required
def get_history(class_id):
    db = get_db()
    rows = db.execute(
        "SELECT id, note, created_by, created_at FROM tt_history WHERE class_id=? ORDER BY id DESC LIMIT 50",
        (class_id,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@api_bp.post("/restore/<int:history_id>")
@admin_required
def restore_history(history_id):
    import json as _json
    db = get_db()
    hist = db.execute("SELECT * FROM tt_history WHERE id=?", (history_id,)).fetchone()
    if not hist:
        return jsonify({"error": "Topilmadi"}), 404

    class_id = hist["class_id"]
    snapshot = _json.loads(hist["snapshot_json"])

    # joriy holatni ham tarixga yozib qo'yamiz (restore ham qaytariladigan bo'lsin)
    save_history(db, class_id, "Restore'dan oldingi holat", session.get("username", "admin"))

    db.execute("DELETE FROM tt_lessons WHERE class_id=?", (class_id,))
    for l in snapshot:
        db.execute(
            """
            INSERT INTO tt_lessons (class_id, day_of_week, slot_order, subject_id, teacher_id, room_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (l["class_id"], l["day_of_week"], l["slot_order"],
             l["subject_id"], l["teacher_id"], l["room_id"]),
        )
    db.commit()
    realtime.broadcast("lesson_changed", {"class_id": class_id})
    return jsonify({"ok": True, "restored_lessons": len(snapshot)})


# ------------------------------------------------------------------
# Real-time (SSE)
# ------------------------------------------------------------------
@api_bp.get("/stream")
@login_required_api
def stream():
    from flask import Response
    return Response(realtime.sse_stream(), mimetype="text/event-stream")


# ------------------------------------------------------------------
# Import / Export
# ------------------------------------------------------------------
@api_bp.get("/export/excel/<int:class_id>")
@login_required_api
def export_excel_route(class_id):
    db = get_db()
    cls = db.execute("SELECT name FROM tt_classes WHERE id=?", (class_id,)).fetchone()
    if not cls:
        return jsonify({"error": "Sinf topilmadi"}), 404
    buf = export_excel(db, class_id, cls["name"])
    return send_file(
        buf, as_attachment=True,
        download_name=f"{cls['name']}-jadval.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@api_bp.get("/export/pdf/<int:class_id>")
@login_required_api
def export_pdf_route(class_id):
    db = get_db()
    cls = db.execute("SELECT name FROM tt_classes WHERE id=?", (class_id,)).fetchone()
    if not cls:
        return jsonify({"error": "Sinf topilmadi"}), 404
    buf = export_pdf(db, class_id, cls["name"])
    return send_file(
        buf, as_attachment=True,
        download_name=f"{cls['name']}-jadval.pdf",
        mimetype="application/pdf",
    )


@api_bp.post("/import/excel/<int:class_id>")
@admin_required
def import_excel_route(class_id):
    if "file" not in request.files:
        return jsonify({"error": "Fayl yuborilmadi"}), 400
    db = get_db()
    imported, errors = import_excel(db, class_id, request.files["file"])
    realtime.broadcast("lesson_changed", {"class_id": class_id})
    return jsonify({"ok": True, "imported": imported, "errors": errors})

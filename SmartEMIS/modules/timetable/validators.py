"""
Avtomatik tekshiruv (conflict validation).

Har bir dars qo'yilishidan/o'zgartirilishidan oldin uch turdagi
to'qnashuv tekshiriladi. Har qanday to'qnashuv topilsa, saqlashga
ruxsat berilmaydi va aniq sabab qaytariladi (frontendda qizil
ogohlantirish sifatida ko'rsatiladi).
"""


def check_conflicts(db, class_id, day_of_week, slot_order, teacher_id, room_id, exclude_lesson_id=None):
    """
    Qaytaradi: ro'yxat, bo'sh bo'lsa — to'qnashuv yo'q.
    Har bir element: {"type": ..., "message": ...}
    """
    conflicts = []
    exclude_clause = "AND l.id != ?" if exclude_lesson_id else ""
    params_base = [day_of_week, slot_order]
    exclude_param = [exclude_lesson_id] if exclude_lesson_id else []

    # 1) Bitta o'qituvchi bir vaqtda ikki sinfda bo'lolmaydi
    row = db.execute(
        f"""
        SELECT l.id, c.name AS class_name
        FROM tt_lessons l
        JOIN tt_classes c ON c.id = l.class_id
        WHERE l.day_of_week = ? AND l.slot_order = ? AND l.teacher_id = ?
          AND l.class_id != ? {exclude_clause}
        """,
        params_base + [teacher_id, class_id] + exclude_param,
    ).fetchone()
    if row:
        conflicts.append({
            "type": "teacher",
            "message": f"O'qituvchi shu vaqtda {row['class_name']} sinfida band"
        })

    # 2) Bitta xona bir vaqtda ikki sinf tomonidan band bo'lolmaydi
    row = db.execute(
        f"""
        SELECT l.id, c.name AS class_name
        FROM tt_lessons l
        JOIN tt_classes c ON c.id = l.class_id
        WHERE l.day_of_week = ? AND l.slot_order = ? AND l.room_id = ?
          AND l.class_id != ? {exclude_clause}
        """,
        params_base + [room_id, class_id] + exclude_param,
    ).fetchone()
    if row:
        conflicts.append({
            "type": "room",
            "message": f"Xona shu vaqtda {row['class_name']} sinfi tomonidan band"
        })

    # 3) Bitta sinfda bir vaqtda ikkita fan bo'lolmaydi
    # (UNIQUE(class_id, day_of_week, slot_order) buni bazada ham ta'minlaydi,
    #  lekin bu yerda aniq xabar berish uchun oldindan tekshiramiz)
    row = db.execute(
        f"""
        SELECT l.id, s.name AS subject_name
        FROM tt_lessons l
        JOIN tt_subjects s ON s.id = l.subject_id
        WHERE l.day_of_week = ? AND l.slot_order = ? AND l.class_id = ?
          {exclude_clause}
        """,
        params_base + [class_id] + exclude_param,
    ).fetchone()
    if row:
        conflicts.append({
            "type": "class_slot",
            "message": f"Bu sinfda shu vaqtda allaqachon '{row['subject_name']}' fani bor"
        })

    return conflicts

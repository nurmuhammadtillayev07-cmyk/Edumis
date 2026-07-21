"""
EduMIS — Haftalik Dars Jadvali moduli
Ma'lumotlar bazasi sxemasi va ulanish yordamchilari.

Bu modul asosiy app.py bilan bir xil SQLite faylidan (edumis.db)
foydalanadi, lekin o'z jadvallarini alohida boshqaradi — shu bilan
modul mustaqil (plug-and-play) bo'lib qoladi.
"""
import sqlite3
import json
from datetime import datetime
from flask import g, current_app

DB_PATH = "edumis.db"

# Hafta kunlari: Dushanba(1) ... Shanba(6). Yakshanba ishlatilmaydi.
WEEKDAYS = [
    (1, "Dushanba"),
    (2, "Seshanba"),
    (3, "Chorshanba"),
    (4, "Payshanba"),
    (5, "Juma"),
    (6, "Shanba"),
]


def get_db():
    if "timetable_db" not in g:
        g.timetable_db = sqlite3.connect(DB_PATH)
        g.timetable_db.row_factory = sqlite3.Row
        g.timetable_db.execute("PRAGMA foreign_keys = ON")
    return g.timetable_db


def close_db(exc=None):
    db = g.pop("timetable_db", None)
    if db is not None:
        db.close()


def init_timetable_db():
    """Jadval bilan bog'liq barcha jadvallarni yaratadi (agar mavjud bo'lmasa)."""
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS tt_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tt_teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tt_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL DEFAULT '#2563eb'
        );

        CREATE TABLE IF NOT EXISTS tt_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        -- Dars vaqti slotlari (admin o'zgartira oladi)
        CREATE TABLE IF NOT EXISTS tt_slots (
            slot_order INTEGER PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        );

        -- Har bir katak = bitta sinf + bitta kun + bitta slot
        CREATE TABLE IF NOT EXISTS tt_lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL REFERENCES tt_classes(id) ON DELETE CASCADE,
            day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 6),
            slot_order INTEGER NOT NULL REFERENCES tt_slots(slot_order),
            subject_id INTEGER NOT NULL REFERENCES tt_subjects(id),
            teacher_id INTEGER NOT NULL REFERENCES tt_teachers(id),
            room_id INTEGER NOT NULL REFERENCES tt_rooms(id),
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (class_id, day_of_week, slot_order)
        );

        -- Version history — har bir saqlashda butun sinf jadvali JSON
        -- ko'rinishida saqlanadi, shu orqali Restore qilinadi.
        CREATE TABLE IF NOT EXISTS tt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            snapshot_json TEXT NOT NULL,
            note TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Standart 8 ta dars vaqti slotini boshlang'ich holatda to'ldirish
    existing = db.execute("SELECT COUNT(*) FROM tt_slots").fetchone()[0]
    if existing == 0:
        default_slots = [
            (1, "08:30", "09:15"),
            (2, "09:25", "10:10"),
            (3, "10:20", "11:05"),
            (4, "11:15", "12:00"),
            (5, "12:40", "13:25"),
            (6, "13:35", "14:20"),
            (7, "14:30", "15:15"),
            (8, "15:25", "16:10"),
        ]
        db.executemany(
            "INSERT INTO tt_slots (slot_order, start_time, end_time) VALUES (?, ?, ?)",
            default_slots,
        )

    db.commit()
    db.close()


def snapshot_class(db, class_id):
    """Sinfning joriy haftalik jadvalini JSON snapshot sifatida qaytaradi."""
    rows = db.execute(
        "SELECT * FROM tt_lessons WHERE class_id = ?", (class_id,)
    ).fetchall()
    return json.dumps([dict(r) for r in rows], ensure_ascii=False)


def save_history(db, class_id, note, created_by):
    snap = snapshot_class(db, class_id)
    db.execute(
        "INSERT INTO tt_history (class_id, snapshot_json, note, created_by) VALUES (?, ?, ?, ?)",
        (class_id, snap, note, created_by),
    )

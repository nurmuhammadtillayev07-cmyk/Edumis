"""
Sahifa route'lari — HTML shablonlarni ko'rsatadi.
Ma'lumotlar API orqali (JS fetch bilan) frontendda yuklanadi.
"""
from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for

from .db import get_db, close_db

views_bp = Blueprint("timetable_views", __name__, url_prefix="/timetable")


def login_required_view(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@views_bp.teardown_request
def _teardown(exc):
    close_db(exc)


@views_bp.get("/")
@login_required_view
def timetable_home():
    """Rolga qarab tegishli ko'rinishga yo'naltiradi."""
    role = session.get("role")
    if role == "admin":
        return redirect(url_for("timetable_views.admin_view"))
    return render_template("timetable/view.html", role=role)


@views_bp.get("/admin")
@login_required_view
def admin_view():
    if session.get("role") != "admin":
        return "403 — Sizda bu sahifaga ruxsat yo'q", 403
    return render_template("timetable/admin.html")

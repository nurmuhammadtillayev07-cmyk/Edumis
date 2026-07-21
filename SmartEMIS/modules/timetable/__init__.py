"""
EduMIS — Haftalik Dars Jadvali moduli.

Asosiy app.py'ga ulash uchun:

    from modules.timetable import register_timetable_module
    register_timetable_module(app)
"""
from .db import init_timetable_db
from .api import api_bp
from .views import views_bp


def register_timetable_module(app):
    init_timetable_db()
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

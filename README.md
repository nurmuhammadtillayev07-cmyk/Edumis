# EduMIS

Ta'lim muassasalari uchun boshqaruv tizimi (Flask + SQLite).

## Lokal ishga tushirish

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Brauzerda oching: http://localhost:8080

## Deploy qilish (Render.com)

1. Ushbu repo'ni GitHub'ga push qiling.
2. https://render.com saytida "New +" → "Web Service" tanlang.
3. GitHub repo'ingizni ulang.
4. Sozlamalar avtomatik `render.yaml` fayldan olinadi (Build: `pip install -r requirements.txt`, Start: `gunicorn app:app`).
5. "Create Web Service" tugmasini bosing — bir necha daqiqada sayt tayyor bo'ladi.

**Muhim:** `EDUMIS_SECRET_KEY` environment variable Render tomonidan avtomatik generatsiya qilinadi (xavfsizlik uchun).

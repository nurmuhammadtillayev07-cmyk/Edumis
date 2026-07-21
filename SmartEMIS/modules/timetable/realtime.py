"""
Real-time yangilanish — Server-Sent Events (SSE) orqali.

Eslatma: bu implementatsiya bitta jarayon (single-process dev server yoki
`flask run`) uchun mo'ljallangan — Termux/Pydroid 3 muhitida qo'shimcha
paket (Flask-SocketIO, Redis va h.k.) o'rnatmasdan ishlashi uchun shunday
qilingan. Agar production'da gunicorn bir nechta worker bilan ishga
tushirilsa, xabarlar workerlar orasida tarqalmaydi — shu holatda
Redis pub/sub yoki Flask-SocketIO'ga o'tish tavsiya etiladi
(joylashish-rejasi.md faylida ko'rsatilgandek VPS/production bosqichida).
"""
import json
import queue
import time

_subscribers = []


def subscribe():
    q = queue.Queue(maxsize=50)
    _subscribers.append(q)
    return q


def unsubscribe(q):
    if q in _subscribers:
        _subscribers.remove(q)


def broadcast(event_type, payload):
    data = json.dumps({"type": event_type, "payload": payload}, ensure_ascii=False)
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait(data)
        except queue.Full:
            dead.append(q)
    for q in dead:
        unsubscribe(q)


def sse_stream():
    q = subscribe()
    try:
        # ulanish darhol tasdiqlanadi, keyin har voqeada xabar yuboriladi
        yield "event: connected\ndata: {}\n\n"
        last_ping = time.time()
        while True:
            try:
                data = q.get(timeout=15)
                yield f"data: {data}\n\n"
            except queue.Empty:
                # brauzer ulanishini tirik saqlash uchun ping
                yield ": ping\n\n"
    except GeneratorExit:
        unsubscribe(q)

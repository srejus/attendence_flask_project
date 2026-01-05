import json
import uuid
import os
import base64
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sock import Sock
from werkzeug.utils import secure_filename

# ============================================================
# GLOBAL FLAGS
# ============================================================
ENABLE_DB = False   # <<< THIS IS THE MASTER SWITCH

# ============================================================
# APP INIT
# ============================================================
app = Flask(__name__)
sock = Sock(app)

print("Starting Flask app | DB ENABLED =", ENABLE_DB)

# ============================================================
# OPTIONAL DB SETUP (DISABLED)
# ============================================================
if ENABLE_DB:
    from database import db
    from config.readConf import readConf

    readConf_ = readConf()
    try:
        db_url = readConf_.GetDBParam()
    except Exception as e:
        print("DB config error:", e)
        db_url = None

    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        db.init_app(app)
else:
    db = None
    readConf_ = None

# ============================================================
# HELPERS
# ============================================================
def db_disabled():
    return jsonify({
        "error": "Database is disabled",
        "status": 503
    }), 503

# ============================================================
# BASIC ROUTES (SAFE)
# ============================================================
@app.route("/")
def index():
    return render_template("index.html", APP_PATH=request.base_url[:-1])

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "db_enabled": ENABLE_DB,
        "time": datetime.utcnow().isoformat()
    })

@app.route("/a")
def test_api():
    return jsonify({"key1": "value1", "key2": "value2"})

# ============================================================
# FILE SERVING (SAFE)
# ============================================================
@app.route("/img/<filename>")
def get_image(filename):
    if not ENABLE_DB:
        return db_disabled()

    path = readConf_.GetUploadParam()
    return send_from_directory(path, filename)

# ============================================================
# DB ROUTES (BLOCKED CLEANLY)
# ============================================================
@app.route("/device", methods=["GET", "POST"])
def device_blocked():
    return db_disabled()

@app.route("/records")
def records_blocked():
    return db_disabled()

@app.route("/emps")
def emps_blocked():
    return db_disabled()

# ============================================================
# WEBSOCKET (SAFE – NO DB)
# ============================================================
@sock.route("/")
def ws_root(ws):
    while True:
        data = ws.receive()
        if data is None:
            break
        print("WS:", data)

@sock.route("/pub/chat")
def ws_chat(ws):
    try:
        while True:
            msg = ws.receive()
            if msg is None:
                break

            try:
                payload = json.loads(msg)
            except Exception:
                ws.send(json.dumps({"error": "invalid json"}))
                continue

            cmd = payload.get("cmd", "")
            if cmd == "ping":
                ws.send(json.dumps({"ret": "pong"}))
            else:
                ws.send(json.dumps({"ret": "unknown"}))
    except Exception as e:
        print("WebSocket error:", e)

# ============================================================
# FLASK ENTRYPOINT
# ============================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=7020,
        debug=True
    )

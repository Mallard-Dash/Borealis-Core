"""
api.py — Borealis Core REST API
Wraps the existing CLI backend into HTTP endpoints for the web frontend.
Run:  python3 api.py
Listens on 0.0.0.0:5000
"""

import os
import json
import re
import mariadb
import boto3

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
from botocore.exceptions import ClientError

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "borealis-secret-change-in-prod")
CORS(app, supports_credentials=True, origins=["*"])

# ──────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────

def get_db():
    """Open a fresh MariaDB connection (one per request is fine for this scale)."""
    return mariadb.connect(
        user=os.getenv("DB_USER", "vincent"),
        password=os.getenv("DB_PASSWORD", "chad"),
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "healthlogger"),
    )


def require_auth(f):
    """Decorator: reject if no valid session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated


# ──────────────────────────────────────────────
# Auth endpoints
# ──────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or len(password) < 4:
        return jsonify({"error": "Username required and password must be ≥ 4 characters"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username, passwd) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201
    except mariadb.IntegrityError:
        return jsonify({"error": f"Username '{username}' is already taken"}), 409
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM users WHERE username = ? AND passwd = ?",
            (username, password),
        )
        row = cur.fetchone()
        conn.close()
        if row:
            session["user_id"] = row[0]
            session["username"] = username
            return jsonify({"ok": True, "user_id": row[0], "username": username})
        return jsonify({"error": "Wrong username or password"}), 401
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" in session:
        return jsonify({"user_id": session["user_id"], "username": session["username"]})
    return jsonify({"error": "Not authenticated"}), 401


# ──────────────────────────────────────────────
# Daily data  (maps to daily_data table)
# ──────────────────────────────────────────────

@app.route("/api/daily", methods=["GET"])
@require_auth
def get_daily():
    """Return last N daily entries for the logged-in user."""
    limit = int(request.args.get("limit", 30))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """SELECT entryid, entry_date, user_weight, waist, blood_pressure, mental_state, stress
               FROM daily_data WHERE user_id = ?
               ORDER BY entry_date DESC LIMIT ?""",
            (session["user_id"], limit),
        )
        rows = cur.fetchall()
        conn.close()
        entries = []
        for row in rows:
            entryid, entry_date, weight, waist, bp, mood, stress = row
            entries.append({
                "id": entryid,
                "date": entry_date.strftime("%Y-%m-%d") if entry_date else None,
                "weight": weight,
                "waist": waist,
                "bp": bp,
                "mood": mood,
                "stress": stress,
            })
        return jsonify(entries)
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/daily", methods=["POST"])
@require_auth
def post_daily():
    """Insert a new daily entry. Mirrors enter_values() in main.py."""
    data = request.get_json()
    weight = data.get("weight")
    waist = data.get("waist")
    bp = data.get("bp", "")
    mood = data.get("mood")
    stress = data.get("stress")

    # Validate mood/stress range (same logic as main.py)
    if mood is not None and not (1 <= int(mood) <= 10):
        return jsonify({"error": "Mood must be 1–10"}), 400
    if stress is not None and not (1 <= int(stress) <= 10):
        return jsonify({"error": "Stress must be 1–10"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO daily_data(user_id, user_weight, waist, blood_pressure, mental_state, stress) VALUES(?,?,?,?,?,?)",
            (session["user_id"], weight, waist, bp, mood, stress),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"ok": True, "id": new_id}), 201
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Blood pressure convenience endpoint
# Parses bp strings like "118/76-72" and returns structured data
# ──────────────────────────────────────────────

@app.route("/api/bloodpressure", methods=["GET"])
@require_auth
def get_bp():
    """Return parsed BP readings for the chart."""
    limit = int(request.args.get("limit", 30))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT entry_date, blood_pressure FROM daily_data WHERE user_id = ? AND blood_pressure IS NOT NULL AND blood_pressure != '' ORDER BY entry_date ASC LIMIT ?",
            (session["user_id"], limit),
        )
        rows = cur.fetchall()
        conn.close()
        result = []
        for entry_date, bp_str in rows:
            parsed = _parse_bp(bp_str)
            if parsed:
                parsed["date"] = entry_date.strftime("%b %-d") if entry_date else ""
                parsed["full_date"] = entry_date.strftime("%Y-%m-%d") if entry_date else ""
                result.append(parsed)
        return jsonify(result)
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


def _parse_bp(bp_str):
    """Parse strings like '118/76-72' or '118/76' into {sys, dia, pulse}."""
    if not bp_str:
        return None
    m = re.match(r"(\d+)[/\\](\d+)(?:[-–](\d+))?", str(bp_str).strip())
    if m:
        return {
            "sys": int(m.group(1)),
            "dia": int(m.group(2)),
            "pulse": int(m.group(3)) if m.group(3) else None,
        }
    return None


# ──────────────────────────────────────────────
# Diary  (maps to diary table)
# ──────────────────────────────────────────────

@app.route("/api/diary", methods=["GET"])
@require_auth
def get_diary():
    limit = int(request.args.get("limit", 20))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT entry_id, entry_date, content FROM diary WHERE user_id = ? ORDER BY entry_date DESC LIMIT ?",
            (session["user_id"], limit),
        )
        rows = cur.fetchall()
        conn.close()
        return jsonify([
            {"id": r[0], "date": r[1].strftime("%Y-%m-%d %H:%M") if r[1] else "", "content": r[2]}
            for r in rows
        ])
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/diary", methods=["POST"])
@require_auth
def post_diary():
    data = request.get_json()
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Content is required"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO diary(content, user_id) VALUES(?, ?)",
            (content, session["user_id"]),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"ok": True, "id": new_id}), 201
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/diary/<int:entry_id>", methods=["DELETE"])
@require_auth
def delete_diary(entry_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM diary WHERE entry_id = ? AND user_id = ?",
            (entry_id, session["user_id"]),
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Personal Wiki / Knowledge  (maps to knowledge_db)
# ──────────────────────────────────────────────

@app.route("/api/wiki/categories", methods=["GET"])
@require_auth
def get_categories():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT category_id, category_name FROM knowledge_categories ORDER BY category_id")
        rows = cur.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "name": r[1]} for r in rows])
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki", methods=["GET"])
@require_auth
def get_wiki():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """SELECT c.category_id, c.category_name, k.knowledge_content, k.entry_date
               FROM knowledge_db k
               JOIN knowledge_categories c ON k.category_id = c.category_id
               WHERE k.user_id = ?
               ORDER BY k.entry_date DESC""",
            (session["user_id"],),
        )
        rows = cur.fetchall()
        conn.close()
        return jsonify([
            {"category_id": r[0], "category": r[1], "content": r[2],
             "date": r[3].strftime("%Y-%m-%d") if r[3] else ""}
            for r in rows
        ])
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki", methods=["POST"])
@require_auth
def post_wiki():
    data = request.get_json()
    category_id = data.get("category_id")
    content = (data.get("content") or "").strip()
    if not category_id or not content:
        return jsonify({"error": "category_id and content are required"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO knowledge_db(user_id, category_id, knowledge_content) VALUES(?, ?, ?)",
            (session["user_id"], int(category_id), content),
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wiki/<int:category_id>", methods=["DELETE"])
@require_auth
def delete_wiki_entry(category_id):
    """Delete all wiki entries for this user in a given category."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM knowledge_db WHERE user_id = ? AND category_id = ?",
            (session["user_id"], category_id),
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# AI Chat  (calls AWS Bedrock, stores in ai_insights)
# Mirrors call_agent() in bedrock_agent.py exactly
# ──────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "lighthouse": (
        "You are a grizzled 1890s lighthouse keeper: stern, sea-salted language, "
        "dark humor, nautical metaphors, and old-world discipline. "
        "Be intense but still helpful and coherent. Do not quote copyrighted dialogue."
    ),
    "pirate":       "You are a pirate that just lost all crewmembers and seeks revenge",
    "butler":       "You are an overly-polite butler that is a loyal servant to the user, you are old-fashioned",
    "old1895":      "You are an old-fashioned person that still lives in the year 1895",
    "mentor":       "You are a stubborn mentor that won't accept failure. Support the user in whatever they need help with.",
    "coach":        "You are an analytical and professional health-coach. Help the user with health-related questions.",
    "philosopher":  "You are an old-world philosopher with a deep thinking mind and great answers to almost every question.",
    "gymbro":       "You are an aggressive gym-bro whose only goal is to get the user to the gym with inspirational speech.",
    "wizard":       "You are a very wise Wizard from a fantasy realm who speaks in riddles but can be understood.",
    "kevin":        "You are a 90s infomercial host secretly in a really bad mood but won't talk about it. Your name is Kevin and you sometimes beg the user to buy your worthless infomercial product.",
}

MODEL_IDS = {
    "sonnet":  "us.anthropic.claude-sonnet-4-6",
    "opus":    "us.anthropic.claude-opus-4-6-v1",
    "haiku":   "anthropic.claude-haiku-4-5-20251001-v1:0",
    "haiku3":  "anthropic.claude-3-haiku-20240307-v1:0",
}


def _load_health_context(conn, user_id):
    """Mirrors load_health_data + format_health_context from bedrock_agent.py."""
    cur = conn.cursor()
    cur.execute(
        "SELECT entry_date, user_weight, waist, blood_pressure, mental_state, stress FROM daily_data WHERE user_id = ? ORDER BY entry_date DESC LIMIT 10",
        (user_id,),
    )
    rows = cur.fetchall()
    if not rows:
        return "No recent health data available."
    lines = []
    for entry_date, weight, waist, bp, mood, stress in rows:
        lines.append(
            f"{entry_date} | weight: {weight} kg | waist: {waist} cm | "
            f"blood pressure: {bp} | mood: {mood}/10 | stress: {stress}/10"
        )
    return "Recent health data:\n" + "\n".join(lines)


def _load_ai_history(conn, user_id):
    """Mirrors load_history from bedrock_agent.py."""
    cur = conn.cursor()
    cur.execute(
        "SELECT user_query, ai_response FROM ai_insights WHERE user_id = ? ORDER BY created_at DESC LIMIT 15",
        (user_id,),
    )
    return list(reversed(cur.fetchall()))


@app.route("/api/ai/chat", methods=["POST"])
@require_auth
def ai_chat():
    data = request.get_json()
    user_message = (data.get("message") or "").strip()
    persona_key  = data.get("persona", "lighthouse")
    model_key    = data.get("model", "sonnet")
    custom_prompt = data.get("custom_prompt", "")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    base_prompt = custom_prompt if custom_prompt else SYSTEM_PROMPTS.get(persona_key, SYSTEM_PROMPTS["lighthouse"])
    model_id    = MODEL_IDS.get(model_key, MODEL_IDS["sonnet"])

    try:
        conn = get_db()
        health_context = _load_health_context(conn, session["user_id"])
        full_system_prompt = (
            f"{base_prompt}\n\n"
            "The following health data belongs to the current user. "
            "Use it only when relevant — do not invent trends not supported by the data.\n\n"
            f"{health_context}"
        )

        # Build chat history from db  (mirrors call_agent)
        history_rows = _load_ai_history(conn, session["user_id"])
        chat_history = []
        for user_q, ai_r in history_rows:
            chat_history.append({"role": "user",      "content": [{"type": "text", "text": user_q}]})
            chat_history.append({"role": "assistant", "content": [{"type": "text", "text": ai_r}]})
        chat_history.append({"role": "user", "content": [{"type": "text", "text": user_message}]})

        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.5,
            "system": full_system_prompt,
            "messages": chat_history,
        }
        response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
        model_response = json.loads(response["body"].read())
        ai_text = model_response["content"][0]["text"]

        # Persist turn (mirrors persist_turn)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ai_insights(user_id, user_query, ai_response) VALUES(?, ?, ?)",
            (session["user_id"], user_message, ai_text),
        )
        conn.commit()
        conn.close()

        return jsonify({"response": ai_text})

    except ClientError as e:
        return jsonify({"error": f"Bedrock error: {e.response['Error']['Message']}"}), 502
    except mariadb.Error as e:
        return jsonify({"error": f"DB error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/history", methods=["GET"])
@require_auth
def get_ai_history():
    """Return recent AI conversation for the chat panel."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_query, ai_response, created_at FROM ai_insights WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (session["user_id"],),
        )
        rows = cur.fetchall()
        conn.close()
        return jsonify([
            {"user": r[0], "ai": r[1], "at": r[2].strftime("%Y-%m-%d %H:%M") if r[2] else ""}
            for r in reversed(rows)
        ])
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Health profile  — no table exists yet, store as wiki entries
# category_id 4 = Health (from knowledge_categories seed data)
# ──────────────────────────────────────────────

@app.route("/api/healthprofile", methods=["GET"])
@require_auth
def get_health_profile():
    """Load the saved health profile JSON stored as a wiki entry in category 4."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT knowledge_content FROM knowledge_db WHERE user_id = ? AND category_id = 4 ORDER BY entry_date DESC LIMIT 1",
            (session["user_id"],),
        )
        row = cur.fetchone()
        conn.close()
        if row:
            try:
                return jsonify(json.loads(row[0]))
            except Exception:
                return jsonify({"raw": row[0]})
        return jsonify({})
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/healthprofile", methods=["POST"])
@require_auth
def post_health_profile():
    """Save / overwrite health profile as a JSON blob in wiki category 4."""
    data = request.get_json()
    content = json.dumps(data)
    try:
        conn = get_db()
        cur = conn.cursor()
        # Delete existing profile entry so there's always exactly one
        cur.execute(
            "DELETE FROM knowledge_db WHERE user_id = ? AND category_id = 4",
            (session["user_id"],),
        )
        cur.execute(
            "INSERT INTO knowledge_db(user_id, category_id, knowledge_content) VALUES(?, 4, ?)",
            (session["user_id"], content),
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# Training log — stored as wiki entries in category 14 (Fitness)
# Each entry is a JSON blob
# ──────────────────────────────────────────────

@app.route("/api/training", methods=["GET"])
@require_auth
def get_training():
    limit = int(request.args.get("limit", 30))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT knowledge_content, entry_date FROM knowledge_db WHERE user_id = ? AND category_id = 14 ORDER BY entry_date DESC LIMIT ?",
            (session["user_id"], limit),
        )
        rows = cur.fetchall()
        conn.close()
        results = []
        for content, entry_date in rows:
            try:
                obj = json.loads(content)
                if "type" in obj:  # only real training entries
                    results.append(obj)
            except Exception:
                pass
        return jsonify(results)
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/training", methods=["POST"])
@require_auth
def post_training():
    data = request.get_json()
    required = ["date", "type", "duration"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO knowledge_db(user_id, category_id, knowledge_content) VALUES(?, 14, ?)",
            (session["user_id"], json.dumps(data)),
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201
    except mariadb.Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

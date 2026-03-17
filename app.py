import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

# Flask app
app = Flask(__name__, template_folder='html', static_folder='.', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET', 'your_secret_key')

# ---------------- MYSQL CONNECTION ---------------- #

def get_db_connection():
    url = urlparse(os.getenv("MYSQL_URL"))

    return pymysql.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:],  # remove '/'
        port=url.port,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )

# ---------------- SQLITE FALLBACK ---------------- #

sqlite_db_path = Path('dev_fallback.db')
# Default to sqlite when no MYSQL_URL is provided; runtime failures
# when MYSQL_URL is set will be caught where connections are attempted.
use_sqlite = not bool(os.getenv("MYSQL_URL"))

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    try:
        return app.send_static_file('index.html')
    except Exception as e:
        print("INDEX ERROR:", e)
        return "App is running ✅"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('Auth/login.html')

    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')
    role = data.get('role')

    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            if role == 'student':
                cur.execute("SELECT * FROM Student WHERE Student_ID=? AND Password=?", (user_id, password))
            else:
                cur.execute("SELECT * FROM Warden WHERE Warden_ID=? AND Password=?", (user_id, password))
            user = cur.fetchone()
            conn.close()
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            if role == 'student':
                cur.execute("SELECT * FROM Student WHERE Student_ID=%s AND Password=%s", (user_id, password))
            else:
                cur.execute("SELECT * FROM Warden WHERE Warden_ID=%s AND Password=%s", (user_id, password))
            user = cur.fetchone()
            conn.close()

        if user:
            session['user_id'] = user_id
            session['role'] = role
            return jsonify({"success": True})
        else:
            return jsonify({"success": False}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/student/dashboard')
def student_dashboard():
    return render_template('Student/student-dashboard.html')

@app.route('/warden/dashboard')
def warden_dashboard():
    return render_template('Warden/admin-dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- DB TEST ---------------- #

@app.route('/dbtest')
def db_test():
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            return jsonify({"ok": True, "db": "sqlite"})

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return jsonify({"ok": True, "db": "mysql"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- API ---------------- #

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("SELECT Student_ID, Name, Email FROM Student")
            rows = cur.fetchall()
            conn.close()
            data = [{"Student_ID": r[0], "Name": r[1], "Email": r[2]} for r in rows]
            return jsonify(data)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT Student_ID, Name, Email FROM Student")
        data = cur.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- RUN ---------------- #

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
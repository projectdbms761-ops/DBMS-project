import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import os
import sqlite3
from pathlib import Path
from functools import wraps
import random

# Flask app
app = Flask(__name__, template_folder='html', static_folder='.', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET', 'your_secret_key')

# MySQL connection (Railway)
from urllib.parse import urlparse


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

# SQLite fallback
use_sqlite = False
sqlite_db_path = Path('dev_fallback.db')

def init_dev_fallback():
    global use_sqlite
    try:
        conn = get_db_connection()
        conn.close()
        print("MySQL Connected ✅")
    except Exception:
        print("Using SQLite fallback ⚠️")
        use_sqlite = True

init_dev_fallback()

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    try:
        return app.send_static_file('index.html')
    except:
        return render_template('Auth/login.html')

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
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- API ---------------- #

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT Student_ID, Name, Email FROM Student")
        data = cur.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

def init_dev_fallback():
    global use_sqlite
    try:
        conn = get_db_connection()
        print("MYSQL CONNECTED ✅")
        conn.close()
    except Exception as e:
        print("MYSQL ERROR:", e)   # 👈 THIS IS KEY
        use_sqlite = True
# ---------------- RUN ---------------- #

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
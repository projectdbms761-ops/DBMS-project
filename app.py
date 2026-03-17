from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from flask_mysqldb import MySQL
import os
import sqlite3
from pathlib import Path
from functools import wraps
import random

# Path to the canonical SQL schema file (MySQL-ready)
SCHEMA_SQL = Path('database.sql')

# Create Flask app once. Set template_folder to `html` and serve project root
# so existing `css/` and `js/` folders are reachable at `/css/...` and `/js/...`.
app = Flask(__name__, template_folder='html', static_folder='.', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET', 'your_secret_key')

# --- MySQL Configuration (update with real credentials or env vars) ---
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'your_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'hostel_db')

mysql = MySQL(app)

# Development fallback: if MySQL auth fails, use a local SQLite file with sample users
use_sqlite = False
sqlite_db_path = Path('dev_fallback.db')

def init_dev_fallback():
    """Try a quick MySQL probe; if it fails enable a local sqlite fallback with test users."""
    global use_sqlite
    try:
        # Use an application context for MySQL probe to avoid 'working outside' errors
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('SELECT 1')
            cur.close()

            # If we can connect to MySQL, attempt to apply schema.sql to the MySQL server
            try:
                if SCHEMA_SQL.exists():
                    print('MySQL reachable — attempting to apply schema from database.sql')
                    apply_mysql_schema(SCHEMA_SQL)
                else:
                    print('MySQL reachable but database.sql not found; skipping schema apply')
            except Exception as e:
                print('Warning: failed to apply MySQL schema:', e)

            return
    except Exception:
        use_sqlite = True
        conn = sqlite3.connect(sqlite_db_path)
        c = conn.cursor()
        # Enable FK support
        c.execute('PRAGMA foreign_keys = ON')

        # Create tables according to the provided schema
        c.execute('''CREATE TABLE IF NOT EXISTS Student (
            Student_ID TEXT PRIMARY KEY,
            Name TEXT,
            Gender TEXT,
            Phone TEXT,
            Email TEXT,
            Address TEXT,
            Password TEXT,
            Course TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Hostel (
            Hostel_ID TEXT PRIMARY KEY,
            Hostel_Name TEXT,
            Location TEXT,
            Type TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Room (
            Room_ID TEXT PRIMARY KEY,
            Room_Number TEXT,
            Room_Type TEXT,
            Capacity INTEGER,
            Hostel_ID TEXT,
            FOREIGN KEY(Hostel_ID) REFERENCES Hostel(Hostel_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Allocation (
            Allocation_ID TEXT PRIMARY KEY,
            Student_ID TEXT,
            Room_ID TEXT,
            Allotment_Date TEXT,
            FOREIGN KEY(Student_ID) REFERENCES Student(Student_ID),
            FOREIGN KEY(Room_ID) REFERENCES Room(Room_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Fees (
            Fee_ID TEXT PRIMARY KEY,
            Student_ID TEXT,
            Amount REAL,
            Payment_Date TEXT,
            Payment_Status TEXT,
            FOREIGN KEY(Student_ID) REFERENCES Student(Student_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Warden (
            Warden_ID TEXT PRIMARY KEY,
            Name TEXT,
            Phone TEXT,
            Hostel_ID TEXT,
            FOREIGN KEY(Hostel_ID) REFERENCES Hostel(Hostel_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Student_Leave (
            Leave_ID TEXT PRIMARY KEY,
            Student_ID TEXT,
            Leave_Date TEXT,
            Return_Date TEXT,
            Reason TEXT,
            FOREIGN KEY(Student_ID) REFERENCES Student(Student_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Laundry (
            Laundry_ID TEXT PRIMARY KEY,
            Student_ID TEXT,
            Clothes_Count INTEGER,
            Laundry_Date TEXT,
            Charges REAL,
            Status TEXT,
            FOREIGN KEY(Student_ID) REFERENCES Student(Student_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Complaint (
            Complaint_ID TEXT PRIMARY KEY,
            Student_ID TEXT,
            Room_ID TEXT,
            Complaint_Date TEXT,
            Complaint_Type TEXT,
            Description TEXT,
            Status TEXT,
            FOREIGN KEY(Student_ID) REFERENCES Student(Student_ID),
            FOREIGN KEY(Room_ID) REFERENCES Room(Room_ID)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS Maintenance (
            Maintenance_ID TEXT PRIMARY KEY,
            Complaint_ID TEXT,
            Hostel_ID TEXT,
            Maintenance_Date TEXT,
            Work_Type TEXT,
            Cost REAL,
            Status TEXT,
            FOREIGN KEY(Complaint_ID) REFERENCES Complaint(Complaint_ID),
            FOREIGN KEY(Hostel_ID) REFERENCES Hostel(Hostel_ID)
        )''')

        # Insert sample dev data if missing
        try:
            c.execute("INSERT OR IGNORE INTO Student (Student_ID, Name, Gender, Phone, Email, Address, Password, Course) VALUES ('STU101','Test Student','M','+911234567890','test@student.local','123 College Rd','pass123','BSc Computer Science')")
            c.execute("INSERT OR IGNORE INTO Warden (Warden_ID, Name, Phone, Hostel_ID) VALUES ('WRD501','Test Warden','+911112223334','H01')")

            # Seed a sample hostel and rooms if none exist
            c.execute("SELECT COUNT(*) FROM Hostel")
            host_count = c.fetchone()[0]
            if host_count == 0:
                c.execute("INSERT INTO Hostel (Hostel_ID, Hostel_Name, Location, Type) VALUES ('H01','Boys Alpha','North Campus','Boys')")

            c.execute("SELECT COUNT(*) FROM Room")
            room_count = c.fetchone()[0]
            if room_count == 0:
                rooms_to_add = [
                    ('R001','B-201','3-Seater',3,'H01'),
                    ('R002','B-202','3-Seater',3,'H01'),
                    ('R003','B-301','2-Seater (AC)',2,'H01')
                ]
                for r in rooms_to_add:
                    c.execute("INSERT OR IGNORE INTO Room (Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID) VALUES (?,?,?,?,?)", r)

            # Optionally seed an allocation
            c.execute("SELECT COUNT(*) FROM Allocation")
            if c.fetchone()[0] == 0:
                c.execute("INSERT OR IGNORE INTO Allocation (Allocation_ID, Student_ID, Room_ID, Allotment_Date) VALUES ('A001','STU101','R001','2025-08-15')")
        except Exception:
            pass

        conn.commit()
        conn.close()


def apply_mysql_schema(sql_path: Path):
    """Read the SQL file and execute statements against the configured MySQL connection.
    This is a best-effort helper for local/dev: it will run each statement found in
    `database.sql` sequentially. It requires the MySQL credentials set in app.config.
    """
    if not sql_path.exists():
        raise FileNotFoundError(str(sql_path))

    with app.app_context():
        cur = mysql.connection.cursor()
        sql_text = sql_path.read_text(encoding='utf-8')

        # Basic sanitize: remove /* */ and -- comments lines
        lines = []
        in_block = False
        for raw in sql_text.splitlines():
            line = raw.strip()
            if line.startswith('/*'):
                in_block = True
                continue
            if in_block:
                if line.endswith('*/'):
                    in_block = False
                continue
            if line.startswith('--') or not line:
                continue
            lines.append(raw)

        cleaned = '\n'.join(lines)

        # Split statements by semicolon. This is simple but works for our schema file.
        statements = [s.strip() for s in cleaned.split(';') if s.strip()]

        for stmt in statements:
            try:
                cur.execute(stmt)
            except Exception as e:
                # Log and continue; some statements (like USE) may fail depending on permissions
                print('Warning: failed to execute statement:', stmt[:80].replace('\n',' '), '->', e)

        try:
            mysql.connection.commit()
        except Exception:
            pass
        cur.close()


# Initialize fallback at startup
init_dev_fallback()


def ensure_sqlite_seed():
    """Always ensure the local SQLite dev DB has minimal seed data for UI testing.
    This runs even if MySQL is available so the developer UI can show example rows.
    """
    conn = sqlite3.connect(sqlite_db_path)
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    # create minimal tables if missing (idempotent)
    c.execute('''CREATE TABLE IF NOT EXISTS Hostel (Hostel_ID TEXT PRIMARY KEY, Hostel_Name TEXT, Location TEXT, Type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Room (Room_ID TEXT PRIMARY KEY, Room_Number TEXT, Room_Type TEXT, Capacity INTEGER, Hostel_ID TEXT, FOREIGN KEY(Hostel_ID) REFERENCES Hostel(Hostel_ID))''')
    c.execute('''CREATE TABLE IF NOT EXISTS Student (Student_ID TEXT PRIMARY KEY, Name TEXT, Gender TEXT, Phone TEXT, Email TEXT, Address TEXT, Password TEXT, Course TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Allocation (Allocation_ID TEXT PRIMARY KEY, Student_ID TEXT, Room_ID TEXT, Allotment_Date TEXT, FOREIGN KEY(Student_ID) REFERENCES Student(Student_ID), FOREIGN KEY(Room_ID) REFERENCES Room(Room_ID))''')

    # seed hostel if missing
    c.execute("SELECT COUNT(*) FROM Hostel")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO Hostel (Hostel_ID, Hostel_Name, Location, Type) VALUES ('H01','Boys Alpha','North Campus','Boys')")

    # seed rooms if missing
    c.execute("SELECT COUNT(*) FROM Room")
    if c.fetchone()[0] == 0:
        rooms_to_add = [
            ('R001','B-201','3-Seater',3,'H01'),
            ('R002','B-202','3-Seater',3,'H01'),
            ('R003','B-301','2-Seater (AC)',2,'H01')
        ]
        for r in rooms_to_add:
            try:
                c.execute("INSERT OR IGNORE INTO Room (Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID) VALUES (?,?,?,?,?)", r)
            except Exception:
                pass

    # seed student if missing
    c.execute("SELECT COUNT(*) FROM Student")
    if c.fetchone()[0] == 0:
        c.execute("INSERT OR IGNORE INTO Student (Student_ID, Name, Gender, Phone, Email, Address, Password, Course) VALUES ('STU101','Test Student','M','+911234567890','test@student.local','123 College Rd','pass123','BSc Computer Science')")

    # seed allocation if missing
    c.execute("SELECT COUNT(*) FROM Allocation")
    if c.fetchone()[0] == 0:
        try:
            c.execute("INSERT OR IGNORE INTO Allocation (Allocation_ID, Student_ID, Room_ID, Allotment_Date) VALUES ('A001','STU101','R001','2025-08-15')")
        except Exception:
            pass

    conn.commit()
    conn.close()


ensure_sqlite_seed()


@app.route('/')
def index():
    # templates live under the `html/` folder; use forward slashes and paths
    # relative to that folder.
    # Serve the main landing page located at the project root `index.html`.
    # `static_folder='.'` is configured, so use `send_static_file` to return it.
    try:
        return app.send_static_file('index.html')
    except Exception:
        # Fallback to the login template if the landing page is missing.
        return render_template('Auth/login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Support GET so a browser navigation to /login doesn't return 404/405.
    if request.method == 'GET':
        return render_template('Auth/login.html')

    data = request.get_json() or {}
    user_id = data.get('id')
    password = data.get('password')
    role = data.get('role')

    try:
        # Use sqlite fallback if enabled
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            if role == 'student':
                cur.execute("SELECT * FROM Student WHERE Student_ID = ? AND Password = ?", (user_id, password))
            else:
                cur.execute("SELECT * FROM Warden WHERE Warden_ID = ? AND Password = ?", (user_id, password))
            user = cur.fetchone()
            cur.close()
            conn.close()
        else:
            cursor = mysql.connection.cursor()
            if role == 'student':
                cursor.execute("SELECT * FROM Student WHERE Student_ID = %s AND Password = %s", (user_id, password))
            else:
                cursor.execute("SELECT * FROM Warden WHERE Warden_ID = %s AND Password = %s", (user_id, password))
            user = cursor.fetchone()
            cursor.close()

        if user:
            session['user_id'] = user_id
            session['role'] = role
            return jsonify({"success": True, "role": role})
        else:
            return jsonify({"success": False, "message": "Invalid Credentials"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": f"DB error: {str(e)}"}), 500


# Simple routes to serve dashboards (static templates exist under html/)
@app.route('/student/dashboard')
def student_dashboard():
    return render_template('Student/student-dashboard.html')


@app.route('/warden/dashboard')
def warden_dashboard():
    return render_template('Warden/admin-dashboard.html')


# Support legacy static paths that some pages or bookmarks may use and
# redirect them to the Flask route that serves the login page.
@app.route('/Auth/login.html')
@app.route('/html/Auth/login.html')
def legacy_login_paths():
    return redirect(url_for('login'))


# Development helper: test DB connection and show error (do NOT enable in production)
@app.route('/dbtest')
def db_test():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT 1')
        cur.fetchone()
        cur.close()
        return jsonify({"ok": True, "message": "DB connected successfully"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Simple session/role protection decorator
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
                if role:
                    # Accept both 'admin' and 'warden' as warden-level roles
                    if role == 'warden':
                        if session.get('role') not in ('warden', 'admin'):
                            return abort(403)
                    else:
                        if session.get('role') != role:
                            return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Serve any Warden page under /warden/ by rendering the corresponding template.
@app.route('/warden/<path:page>')
@login_required(role='warden')
def warden_pages(page):
    # Prevent path traversal
    if '..' in page or page.startswith('/'):
        return abort(404)
    # If a request asks for e.g. 'admin-students.html', render that file from html/Warden
    return render_template(f'Warden/{page}')


# API: Students - basic CRUD (protected for wardens)
@app.route('/api/students', methods=['GET', 'POST'])
@login_required(role='warden')
def api_students():
    if request.method == 'GET':
        try:
            if use_sqlite:
                conn = sqlite3.connect(sqlite_db_path)
                cur = conn.cursor()
                cur.execute("SELECT Student_ID, Name, Course, Email FROM Student")
                rows = cur.fetchall()
                cur.close()
                conn.close()
                students = [{"id": r[0], "name": r[1], "course": r[2], "email": r[3]} for r in rows]
            else:
                cur = mysql.connection.cursor()
                cur.execute("SELECT Student_ID, Name, Course, Email FROM Student")
                rows = cur.fetchall()
                cur.close()
                students = [{"id": r[0], "name": r[1], "course": r[2], "email": r[3]} for r in rows]
            return jsonify({"students": students})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # POST - create a new student
    data = request.get_json() or {}
    sid = data.get('id') or f"STU{random.randint(1000,9999)}"
    name = data.get('name')
    course = data.get('course')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password', 'changeme')
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO Student (Student_ID, Name, Password, Course, Email, Phone) VALUES (?,?,?,?,?,?)",
                        (sid, name, password, course, email, phone))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Student (Student_ID, Name, Password, Course, Email, Phone) VALUES (%s,%s,%s,%s,%s,%s)",
                        (sid, name, password, course, email, phone))
            mysql.connection.commit()
            cur.close()
        return jsonify({"ok": True, "id": sid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/students/<student_id>', methods=['DELETE'])
@login_required(role='warden')
def api_delete_student(student_id):
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM Student WHERE Student_ID = ?", (student_id,))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM Student WHERE Student_ID = %s", (student_id,))
            mysql.connection.commit()
            cur.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Rooms API
@app.route('/api/rooms', methods=['GET', 'POST'])
@login_required(role='warden')
def api_rooms():
    if request.method == 'GET':
        try:
            rooms = []
            if use_sqlite:
                conn = sqlite3.connect(sqlite_db_path)
                cur = conn.cursor()
                cur.execute("SELECT Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID FROM Room")
                rows = cur.fetchall()
                for r in rows:
                    room_id = r[0]
                    cur.execute("SELECT COUNT(*) FROM Allocation WHERE Room_ID = ?", (room_id,))
                    occ = cur.fetchone()[0]
                    rooms.append({"id": room_id, "number": r[1], "type": r[2], "capacity": r[3], "hostel_id": r[4], "occupied": occ})
                cur.close()
                conn.close()
            else:
                cur = mysql.connection.cursor()
                cur.execute("SELECT Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID FROM Room")
                rows = cur.fetchall()
                for r in rows:
                    room_id = r[0]
                    cur2 = mysql.connection.cursor()
                    cur2.execute("SELECT COUNT(*) FROM Allocation WHERE Room_ID = %s", (room_id,))
                    occ = cur2.fetchone()[0]
                    cur2.close()
                    rooms.append({"id": room_id, "number": r[1], "type": r[2], "capacity": r[3], "hostel_id": r[4], "occupied": occ})
                cur.close()
            return jsonify({"rooms": rooms})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # POST - create room
    data = request.get_json() or {}
    rid = data.get('id') or f"R{random.randint(1000,9999)}"
    number = data.get('number')
    rtype = data.get('type')
    capacity = data.get('capacity') or 1
    hostel_id = data.get('hostel_id')
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO Room (Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID) VALUES (?,?,?,?,?)", (rid, number, rtype, capacity, hostel_id))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Room (Room_ID, Room_Number, Room_Type, Capacity, Hostel_ID) VALUES (%s,%s,%s,%s,%s)", (rid, number, rtype, capacity, hostel_id))
            mysql.connection.commit()
            cur.close()
        return jsonify({"ok": True, "id": rid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rooms/<room_id>', methods=['DELETE'])
@login_required(role='warden')
def api_delete_room(room_id):
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM Room WHERE Room_ID = ?", (room_id,))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM Room WHERE Room_ID = %s", (room_id,))
            mysql.connection.commit()
            cur.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Allocation API
@app.route('/api/allocations', methods=['GET', 'POST'])
@login_required(role='warden')
def api_allocations():
    if request.method == 'GET':
        room = request.args.get('room')
        try:
            allocs = []
            if use_sqlite:
                conn = sqlite3.connect(sqlite_db_path)
                cur = conn.cursor()
                if room:
                    cur.execute("SELECT Allocation_ID, Student_ID, Room_ID, Allotment_Date FROM Allocation WHERE Room_ID = ?", (room,))
                else:
                    cur.execute("SELECT Allocation_ID, Student_ID, Room_ID, Allotment_Date FROM Allocation")
                rows = cur.fetchall()
                for r in rows:
                    allocs.append({"id": r[0], "student_id": r[1], "room_id": r[2], "date": r[3]})
                cur.close()
                conn.close()
            else:
                cur = mysql.connection.cursor()
                if room:
                    cur.execute("SELECT Allocation_ID, Student_ID, Room_ID, Allotment_Date FROM Allocation WHERE Room_ID = %s", (room,))
                else:
                    cur.execute("SELECT Allocation_ID, Student_ID, Room_ID, Allotment_Date FROM Allocation")
                rows = cur.fetchall()
                for r in rows:
                    allocs.append({"id": r[0], "student_id": r[1], "room_id": r[2], "date": r[3]})
                cur.close()
            return jsonify({"allocations": allocs})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # POST - create allocation
    data = request.get_json() or {}
    aid = data.get('id') or f"A{random.randint(1000,9999)}"
    student_id = data.get('student_id')
    room_id = data.get('room_id')
    date = data.get('date') or None
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO Allocation (Allocation_ID, Student_ID, Room_ID, Allotment_Date) VALUES (?,?,?,?)", (aid, student_id, room_id, date))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Allocation (Allocation_ID, Student_ID, Room_ID, Allotment_Date) VALUES (%s,%s,%s,%s)", (aid, student_id, room_id, date))
            mysql.connection.commit()
            cur.close()
        return jsonify({"ok": True, "id": aid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/allocations/<alloc_id>', methods=['DELETE'])
@login_required(role='warden')
def api_delete_allocation(alloc_id):
    try:
        if use_sqlite:
            conn = sqlite3.connect(sqlite_db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM Allocation WHERE Allocation_ID = ?", (alloc_id,))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM Allocation WHERE Allocation_ID = %s", (alloc_id,))
            mysql.connection.commit()
            cur.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
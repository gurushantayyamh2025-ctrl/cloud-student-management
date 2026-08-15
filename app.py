from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path("students.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = get_db()
    students = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    courses = conn.execute("SELECT COUNT(DISTINCT course) FROM students").fetchone()[0]
    conn.close()
    return render_template("index.html", students=students, total=total, courses=courses)

@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    usn = request.form["usn"].strip()
    course = request.form["course"].strip()
    email = request.form["email"].strip()

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO students (name, usn, course, email) VALUES (?, ?, ?, ?)",
            (name, usn, course, email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
    return redirect(url_for("home"))

@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/health")
def health():
    return "Cloud Student Management System - Application is running successfully."

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

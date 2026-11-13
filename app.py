
from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = "database/preppath.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLES ----------------

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'Applied'
        )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- DASHBOARD ----------------

@app.route("/api/dashboard")
def dashboard():
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    ).fetchone()[0]

    aptitude = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE category='Aptitude'"
    ).fetchone()[0]

    coding = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE category='Coding'"
    ).fetchone()[0]

    interviews = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE category='Interview'"
    ).fetchone()[0]

    companies = conn.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    conn.close()

    progress = round((completed / total) * 100) if total else 0

    return jsonify({
        "total": total,
        "completed": completed,
        "aptitude": aptitude,
        "coding": coding,
        "interviews": interviews,
        "companies": companies,
        "progress": progress
    })


# ---------------- GET ALL TASKS ----------------

@app.route("/api/tasks")
def get_tasks():
    category = request.args.get("category")

    conn = get_db()

    if category:
        tasks = conn.execute(
            "SELECT * FROM tasks WHERE category=? ORDER BY id DESC",
            (category,)
        ).fetchall()
    else:
        tasks = conn.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    conn.close()

    return jsonify([dict(task) for task in tasks])


# ---------------- ADD TASK ----------------

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()

    category = data.get("category")
    title = data.get("title")
    difficulty = data.get("difficulty", "Medium")

    if category not in ["Aptitude", "Coding", "Interview"]:
        return jsonify({"error": "Invalid category"}), 400

    if not title or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO tasks (category, title, difficulty)
        VALUES (?, ?, ?)
    """, (category, title.strip(), difficulty))

    conn.commit()
    conn.close()

    return jsonify({"message": "Task added successfully"}), 201


# ---------------- UPDATE TASK STATUS ----------------

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    status = data.get("status")

    if status not in ["Pending", "Completed"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()

    cursor = conn.execute("""
        UPDATE tasks
        SET status=?
        WHERE id=?
    """, (status, task_id))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task updated successfully"})


# ---------------- DELETE TASK ----------------

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted successfully"})


# ---------------- GET COMPANIES ----------------

@app.route("/api/companies")
def get_companies():
    conn = get_db()

    companies = conn.execute(
        "SELECT * FROM companies ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(company) for company in companies])


# ---------------- ADD COMPANY ----------------

@app.route("/api/companies", methods=["POST"])
def add_company():
    data = request.get_json()

    name = data.get("name")
    role = data.get("role")
    status = data.get("status", "Applied")

    if not name or not role:
        return jsonify({"error": "Company and role are required"}), 400

    if status not in ["Applied", "Assessment", "Interview", "Selected", "Rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()

    conn.execute("""
        INSERT INTO companies (name, role, status)
        VALUES (?, ?, ?)
    """, (name.strip(), role.strip(), status))

    conn.commit()
    conn.close()

    return jsonify({"message": "Company added successfully"}), 201


# ---------------- DELETE COMPANY ----------------

@app.route("/api/companies/<int:company_id>", methods=["DELETE"])
def delete_company(company_id):
    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM companies WHERE id=?",
        (company_id,)
    )

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({"message": "Company deleted successfully"})


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

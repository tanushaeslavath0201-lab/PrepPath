import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get(
    "DB_PATH", str(BASE_DIR / "database" / "preppath.db")
))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ================= QUIZ QUESTIONS =================

QUIZZES = {
    "aptitude": {
        "title": "Aptitude",
        "topics": {
            "Percentages": [
                ("What is 20% of 250?", ["25", "40", "50", "60"], 2,
                 "20% of 250 = 50."),
                ("A number increases from 80 to 100. What is the percentage increase?",
                 ["20%", "25%", "30%", "15%"], 1,
                 "Increase = 20/80 × 100 = 25%."),
                ("25% of a number is 45. Find the number.",
                 ["120", "160", "180", "200"], 2,
                 "45 ÷ 0.25 = 180."),
                ("An ₹800 item has a 10% discount. What is its sale price?",
                 ["₹700", "₹720", "₹740", "₹760"], 1,
                 "10% of ₹800 is ₹80. Sale price = ₹720."),
                ("If 40% of x is 120, find x.",
                 ["240", "280", "300", "320"], 2,
                 "120 ÷ 0.4 = 300.")
            ],
            "Time and Work": [
                ("A finishes a job in 10 days. What part is done in one day?",
                 ["1/5", "1/10", "1/15", "1/20"], 1,
                 "One-day work = 1/10."),
                ("A completes work in 6 days and B in 3 days. How long together?",
                 ["1 day", "2 days", "3 days", "4 days"], 1,
                 "Combined rate = 1/6 + 1/3 = 1/2. Answer = 2 days."),
                ("5 workers finish a job in 12 days. How many worker-days?",
                 ["50", "55", "60", "65"], 2,
                 "5 × 12 = 60 worker-days."),
                ("A pipe fills a tank in 4 hours. What fraction is filled in 1 hour?",
                 ["1/2", "1/3", "1/4", "1/5"], 2,
                 "One-hour rate = 1/4."),
                ("12 people finish work in 8 days. How long do 6 people need?",
                 ["4 days", "8 days", "12 days", "16 days"], 3,
                 "Half the workers need twice the time: 16 days.")
            ]
        }
    },

    "coding": {
        "title": "Coding",
        "topics": {
            "Python Basics": [
                ("What is the output of print(2 ** 3)?",
                 ["6", "8", "9", "Error"], 1,
                 "The ** operator performs exponentiation: 2³ = 8."),
                ("Which Python data type is immutable?",
                 ["List", "Dictionary", "Set", "Tuple"], 3,
                 "Tuples are immutable."),
                ("What does len('PrepPath') return?",
                 ["7", "8", "9", "10"], 1,
                 "PrepPath contains 8 characters."),
                ("Which keyword defines a function in Python?",
                 ["func", "define", "def", "function"], 2,
                 "Python functions use the def keyword."),
                ("What is the index of the first list element?",
                 ["0", "1", "-1", "2"], 0,
                 "Python uses zero-based indexing.")
            ],
            "Data Structures": [
                ("Which data structure follows LIFO?",
                 ["Queue", "Stack", "Tree", "Graph"], 1,
                 "A stack follows Last In, First Out."),
                ("Which data structure follows FIFO?",
                 ["Stack", "Queue", "Heap", "Tree"], 1,
                 "A queue follows First In, First Out."),
                ("What is binary search's average time complexity?",
                 ["O(n)", "O(log n)", "O(n²)", "O(1)"], 1,
                 "Binary search halves the search space each step."),
                ("Which traversal visits Left, Root, Right?",
                 ["Preorder", "Postorder", "Inorder", "Level order"], 2,
                 "Inorder traversal is Left, Root, Right."),
                ("Which structure is commonly used for BFS?",
                 ["Stack", "Queue", "Array only", "Hash set"], 1,
                 "BFS uses a queue.")
            ]
        }
    },

    "interview": {
        "title": "Interview",
        "topics": {
            "Technical Fundamentals": [
                ("What does SQL stand for?",
                 ["Structured Query Language", "Simple Question Language",
                  "Sequential Query Logic", "System Query Link"], 0,
                 "SQL stands for Structured Query Language."),
                ("Which OOP concept hides implementation details?",
                 ["Inheritance", "Encapsulation", "Polymorphism", "Compilation"], 1,
                 "Encapsulation bundles data and methods and controls access."),
                ("Which HTTP method is commonly used to retrieve data?",
                 ["POST", "PUT", "GET", "DELETE"], 2,
                 "GET requests retrieve a resource."),
                ("What is the primary purpose of Git?",
                 ["Database storage", "Version control", "UI design",
                  "Cloud hosting"], 1,
                 "Git tracks changes in source code."),
                ("Which SQL clause filters grouped records?",
                 ["WHERE", "ORDER BY", "HAVING", "SELECT"], 2,
                 "HAVING filters groups after aggregation.")
            ],
            "HR Questions": [
                ("What should you do if you do not know an interview answer?",
                 ["Guess confidently", "Be honest and explain your approach",
                  "Change the topic", "Stay silent"], 1,
                 "Be honest and explain what you know."),
                ("How should you answer 'Tell me about yourself'?",
                 ["Unrelated personal details",
                  "A concise education, skills, and project summary",
                  "Read your entire resume", "Discuss salary first"], 1,
                 "Give a concise professional introduction."),
                ("What should you do before an interview?",
                 ["Research the company and role", "Avoid reviewing projects",
                  "Arrive late", "Memorize unrelated facts"], 0,
                 "Research the company, role, and your projects."),
                ("How should you describe a weakness?",
                 ["Say you have none", "Name a real area and how you improve",
                  "Blame others", "Avoid the question"], 1,
                 "Show self-awareness and a practical improvement plan."),
                ("What is a professional response to feedback?",
                 ["Argue immediately", "Ignore it",
                  "Listen and act on useful feedback", "Blame teammates"], 2,
                 "Listen constructively and use feedback to improve.")
            ]
        }
    }
}


# ================= DATABASE =================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)

    db.execute("""
        CREATE TABLE IF NOT EXISTS company_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS quiz_progress (
            section TEXT NOT NULL,
            topic TEXT NOT NULL,
            best_score INTEGER NOT NULL DEFAULT 0,
            latest_score INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(section, topic)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    db.close()


def safe_quizzes():
    return {
        section: {
            "title": data["title"],
            "topics": {
                topic: [
                    {"question": q[0], "options": q[1]}
                    for q in questions
                ]
                for topic, questions in data["topics"].items()
            }
        }
        for section, data in QUIZZES.items()
    }


# ================= MAIN PAGE =================

@app.route("/")
def home():
    return render_template("index.html")


# ================= QUIZ API =================

@app.get("/api/quizzes")
def quizzes_api():
    return jsonify(safe_quizzes())


@app.get("/api/progress")
def progress_api():
    rows = get_db().execute("""
        SELECT section, topic, best_score, latest_score, status, attempts
        FROM quiz_progress
    """).fetchall()

    saved = {
        (r["section"], r["topic"]): dict(r)
        for r in rows
    }

    result = {}
    total = 0
    completed = 0

    for section, data in QUIZZES.items():
        result[section] = {}

        for topic in data["topics"]:
            total += 1

            item = saved.get((section, topic), {
                "section": section,
                "topic": topic,
                "best_score": 0,
                "latest_score": 0,
                "status": "Pending",
                "attempts": 0
            })

            if item["status"] == "Completed":
                completed += 1

            result[section][topic] = item

    return jsonify({
        "topics": result,
        "completed": completed,
        "total": total,
        "percentage": round(completed / total * 100) if total else 0
    })


@app.post("/api/submit-quiz")
def submit_quiz():
    data = request.get_json(silent=True) or {}

    section = data.get("section")
    topic = data.get("topic")
    answers = data.get("answers", {})

    if section not in QUIZZES or topic not in QUIZZES[section]["topics"]:
        return jsonify({"error": "Invalid quiz topic."}), 400

    questions = QUIZZES[section]["topics"][topic]

    if not isinstance(answers, dict) or len(answers) != len(questions):
        return jsonify({"error": "Please answer every question."}), 400

    correct = 0
    review = []

    for i, q in enumerate(questions):
        try:
            selected = int(answers[str(i)])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "Please answer every question."}), 400

        if selected < 0 or selected >= len(q[1]):
            return jsonify({"error": "Invalid answer option."}), 400

        is_correct = selected == q[2]
        correct += int(is_correct)

        review.append({
            "question": q[0],
            "selected": selected,
            "correct": q[2],
            "is_correct": is_correct,
            "explanation": q[3]
        })

    total = len(questions)
    score = round(correct / total * 100)

    # 100% = Completed; below 100% = Pending
    status = "Completed" if score == 100 else "Pending"

    db = get_db()

    old = db.execute("""
        SELECT best_score, attempts
        FROM quiz_progress
        WHERE section=? AND topic=?
    """, (section, topic)).fetchone()

    best = max(score, old["best_score"] if old else 0)
    attempts = (old["attempts"] if old else 0) + 1

    db.execute("""
        INSERT INTO quiz_progress
        (section, topic, best_score, latest_score, status, attempts, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)

        ON CONFLICT(section, topic) DO UPDATE SET
            best_score=excluded.best_score,
            latest_score=excluded.latest_score,
            status=excluded.status,
            attempts=excluded.attempts,
            updated_at=CURRENT_TIMESTAMP
    """, (section, topic, best, score, status, attempts))

    db.execute("""
        INSERT INTO quiz_attempts(section, topic, score, total)
        VALUES (?, ?, ?, ?)
    """, (section, topic, score, total))

    db.commit()

    return jsonify({
        "correct": correct,
        "total": total,
        "score": score,
        "status": status,
        "review": review
    })


# ================= COMPANY TRACKER =================

@app.get("/api/companies")
def companies_api():
    rows = get_db().execute("""
        SELECT id, company, role, status
        FROM company_applications
        ORDER BY id DESC
    """).fetchall()

    return jsonify([dict(r) for r in rows])


@app.post("/api/companies")
def add_company():
    data = request.get_json(silent=True) or {}

    company = (data.get("company") or "").strip()
    role = (data.get("role") or "").strip()
    status = (data.get("status") or "Applied").strip()

    allowed = [
        "Applied", "Assessment", "Interview",
        "Selected", "Rejected"
    ]

    if not company or not role:
        return jsonify({
            "error": "Enter company name and job role."
        }), 400

    if status not in allowed:
        return jsonify({"error": "Invalid status."}), 400

    db = get_db()

    cur = db.execute("""
        INSERT INTO company_applications(company, role, status)
        VALUES (?, ?, ?)
    """, (company, role, status))

    db.commit()

    return jsonify({
        "id": cur.lastrowid,
        "company": company,
        "role": role,
        "status": status
    })


@app.put("/api/companies/<int:company_id>")
def update_company(company_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    allowed = [
        "Applied", "Assessment", "Interview",
        "Selected", "Rejected"
    ]

    if status not in allowed:
        return jsonify({"error": "Invalid status."}), 400

    db = get_db()

    db.execute("""
        UPDATE company_applications
        SET status=?
        WHERE id=?
    """, (status, company_id))

    db.commit()

    return jsonify({"success": True})


@app.delete("/api/companies/<int:company_id>")
def delete_company(company_id):
    db = get_db()

    db.execute(
        "DELETE FROM company_applications WHERE id=?",
        (company_id,)
    )

    db.commit()

    return jsonify({"success": True})


# ================= START APPLICATION =================

init_db()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
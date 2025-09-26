# enhanced_features.py
"""Enhanced features for SIS Dashboard"""

import sqlite3
from datetime import datetime
from typing import Optional

print("Loading enhanced features...")


# Create database
def init_db():
    conn = sqlite3.connect('sis_requirements.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        pegs_category TEXT,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT,
        budget REAL,
        timeline_weeks INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY,
        provider TEXT,
        message TEXT,
        response TEXT,
        created_at TIMESTAMP
    )''')

    # Add default project
    c.execute("SELECT COUNT(*) FROM projects")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO projects (name, budget, timeline_weeks) 
                     VALUES ('SIS Project', 2500000, 29)""")

    conn.commit()
    conn.close()


# Initialize database
init_db()


# PEGS classifier
def classify_pegs(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["timeline", "budget", "schedule"]):
        return "Project"
    elif any(w in text_lower for w in ["compliance", "ferpa", "gdpr"]):
        return "Environment"
    elif any(w in text_lower for w in ["goal", "objective", "roi"]):
        return "Goals"
    else:
        return "System"


# Main function to add endpoints
def add_enhanced_endpoints(app):
    """Add enhanced endpoints to FastAPI app"""

    @app.get("/api/test")
    def test():
        return {"status": "Enhanced features active!", "version": "3.0"}

    @app.get("/api/db/status")
    def db_status():
        try:
            conn = sqlite3.connect('sis_requirements.db')
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM requirements")
            count = c.fetchone()[0]
            conn.close()
            return {"status": "connected", "requirements": count}
        except:
            return {"status": "error"}

    @app.post("/api/requirements/store")
    async def store_req(data: dict):
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()

        category = classify_pegs(data.get("description", ""))

        c.execute(
            """INSERT INTO requirements (title, description, pegs_category, priority)
                     VALUES (?, ?, ?, ?)""",
            (data.get("title", ""), data.get(
                "description", ""), category, data.get("priority", "Medium")))

        conn.commit()
        req_id = c.lastrowid
        conn.close()

        return {"id": req_id, "category": category, "status": "stored"}

    @app.get("/api/requirements/list")
    def list_reqs():
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()
        c.execute("SELECT * FROM requirements")

        reqs = []
        for row in c.fetchall():
            reqs.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "pegs_category": row[3],
                "priority": row[4],
                "status": row[5]
            })

        conn.close()
        return {"count": len(reqs), "requirements": reqs}

    @app.get("/api/pegs/stats")
    def pegs_stats():
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM requirements")
        total = c.fetchone()[0]

        c.execute(
            "SELECT pegs_category, COUNT(*) FROM requirements GROUP BY pegs_category"
        )
        by_category = {}
        for row in c.fetchall():
            if row[0]:
                by_category[row[0]] = row[1]

        conn.close()
        return {"total": total, "by_category": by_category}

    print("✅ Enhanced endpoints added!")
    return app


print("✅ Enhanced features module ready!")

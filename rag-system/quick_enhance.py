# quick_enhance.py
"""
Run this FIRST to create the enhanced_features.py file
"""

print("Creating enhanced_features.py...")

enhancement_code = '''# enhanced_features.py
"""Enhanced features for SIS v2.1.1"""

import sqlite3
from datetime import datetime
from typing import Optional

# Initialize database
def init_db():
    conn = sqlite3.connect('sis_requirements.db')
    c = conn.cursor()

    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS requirements
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT, description TEXT, pegs_category TEXT,
                  priority TEXT, status TEXT DEFAULT 'Draft',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);\'\'\')

    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS chat_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  provider TEXT, message TEXT, response TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);\'\'\')

    conn.commit()
    conn.close()

init_db()

# PEGS Classifier
def classify_pegs(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["timeline", "budget", "schedule"]):
        return "Project"
    elif any(w in text_lower for w in ["compliance", "ferpa", "gdpr"]):
        return "Environment"
    elif any(w in text_lower for w in ["goal", "target", "roi"]):
        return "Goals"
    else:
        return "System"

# Add endpoints to app
def add_enhanced_endpoints(app):
    """Add enhanced endpoints to FastAPI app"""

    @app.get("/api/db/status")
    async def db_status():
        try:
            conn = sqlite3.connect('sis_requirements.db')
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM requirements")
            count = c.fetchone()[0]
            conn.close()
            return {"status": "connected", "requirements": count}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @app.post("/api/requirements/store")
    async def store_requirement(data: dict):
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()

        category = classify_pegs(data.get("description", ""))

        c.execute("""INSERT INTO requirements (title, description, pegs_category, priority) 
                     VALUES (?, ?, ?, ?)""",
                  (data.get("title", ""), data.get("description", ""), 
                   category, data.get("priority", "Medium")))
        conn.commit()
        req_id = c.lastrowid
        conn.close()

        return {"status": "success", "id": req_id, "category": category}

    @app.get("/api/requirements/list")
    async def list_requirements():
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()
        c.execute("SELECT * FROM requirements ORDER BY created_at DESC")

        requirements = []
        for row in c.fetchall():
            requirements.append({
                "id": row[0], "title": row[1], "description": row[2],
                "pegs_category": row[3], "priority": row[4], "status": row[5]
            })
        conn.close()

        return {"count": len(requirements), "requirements": requirements}

    @app.get("/api/pegs/stats")
    async def pegs_stats():
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()

        stats = {"total": 0, "by_category": {}}

        c.execute("SELECT COUNT(*) FROM requirements")
        stats["total"] = c.fetchone()[0]

        c.execute("SELECT pegs_category, COUNT(*) FROM requirements GROUP BY pegs_category")
        for row in c.fetchall():
            stats["by_category"][row[0] if row[0] else "Uncategorized"] = row[1]

        conn.close()
        return stats

    print("✅ Enhanced endpoints added!")
    return app
'''

# Write the file
with open('enhanced_features.py', 'w') as f:
    f.write(enhancement_code)

print("✅ Created enhanced_features.py successfully!")
print("\nNow you can:")
print("1. Add to app.py: from enhanced_features import add_enhanced_endpoints")
print("2. After app = FastAPI(), add: add_enhanced_endpoints(app)")
print("3. Save and run!"
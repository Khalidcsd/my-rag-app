# run_this.py
"""
Just click Run button while this file is open!
This will create all the enhancement files.
"""

print("=" * 60)
print("🚀 CREATING ENHANCED FEATURES")
print("=" * 60)

# Create enhanced_features.py
enhancement_code = '''# enhanced_features.py
import sqlite3
from datetime import datetime
from typing import Optional

def init_database():
    conn = sqlite3.connect('sis_requirements.db')
    c = conn.cursor()

    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, description TEXT, pegs_category TEXT,
        priority TEXT DEFAULT 'Medium', status TEXT DEFAULT 'Draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\'\'\')

    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY, name TEXT, description TEXT,
        budget REAL, timeline_weeks INTEGER
    )\'\'\')

    c.execute(\'\'\'CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY, provider TEXT, message TEXT, response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\'\'\')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_database()

def classify_pegs(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["timeline", "budget", "schedule", "milestone"]):
        return "Project"
    elif any(w in text_lower for w in ["compliance", "ferpa", "gdpr", "regulation"]):
        return "Environment"
    elif any(w in text_lower for w in ["goal", "objective", "roi", "metric"]):
        return "Goals"
    else:
        return "System"

def add_enhanced_endpoints(app):
    """Add enhanced endpoints to FastAPI app"""

    @app.get("/api/enhanced/test")
    def test_enhanced():
        return {
            "status": "✅ Enhanced features working!",
            "version": "3.0",
            "database": "Connected"
        }

    @app.get("/api/db/status")
    def db_status():
        try:
            conn = sqlite3.connect('sis_requirements.db')
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM requirements")
            count = c.fetchone()[0]
            conn.close()
            return {"database": "connected", "requirements_count": count}
        except Exception as e:
            return {"database": "error", "message": str(e)}

    @app.post("/api/requirements/store")
    async def store_requirement(data: dict):
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()

        category = classify_pegs(data.get("description", ""))

        c.execute("""INSERT INTO requirements (title, description, pegs_category, priority)
                     VALUES (?, ?, ?, ?)""",
                  (data.get("title"), data.get("description"), 
                   category, data.get("priority", "Medium")))

        conn.commit()
        req_id = c.lastrowid
        conn.close()

        return {"status": "stored", "id": req_id, "category": category}

    @app.get("/api/requirements/list")
    def list_requirements():
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()
        c.execute("SELECT * FROM requirements ORDER BY id DESC")

        requirements = []
        for row in c.fetchall():
            requirements.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "pegs_category": row[3],
                "priority": row[4],
                "status": row[5]
            })

        conn.close()
        return {"count": len(requirements), "requirements": requirements}

    @app.get("/api/pegs/stats")
    def pegs_stats():
        conn = sqlite3.connect('sis_requirements.db')
        c = conn.cursor()

        stats = {"total": 0, "by_category": {}}

        c.execute("SELECT COUNT(*) FROM requirements")
        stats["total"] = c.fetchone()[0]

        c.execute("SELECT pegs_category, COUNT(*) FROM requirements GROUP BY pegs_category")
        for row in c.fetchall():
            if row[0]:
                stats["by_category"][row[0]] = row[1]

        conn.close()
        return stats

    print("✅ Enhanced endpoints added to app!")
    return app
'''

# Write enhanced_features.py
with open('enhanced_features.py', 'w') as f:
    f.write(enhancement_code)

print("✅ Created: enhanced_features.py")

# Test if we can import it
try:
    import enhanced_features
    print("✅ Module imports successfully!")
except Exception as e:
    print(f"⚠️ Import test failed: {e}")

print("\n" + "=" * 60)
print("📋 NEXT STEPS:")
print("=" * 60)
print("1. STOP your app (Red Stop button)")
print("2. START it again (Green Run button)")
print("3. You should see: '✅ Enhanced features loaded'")
print("\n🧪 Then test these URLs:")
print("   • /api/enhanced/test")
print("   • /api/db/status")
print("   • /api/requirements/list")
print("=" * 60)
print("\n✅ Setup complete! Restart your app now.")

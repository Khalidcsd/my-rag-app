# setup.py
"""
Run this file directly in Replit instead of using Shell commands
Just create this file and click 'Run' button
"""

import os
import shutil
from datetime import datetime


def create_backup():
    """Create backup of existing files"""
    print("📦 Creating backups...")

    # Create backups directory
    if not os.path.exists('backups'):
        os.makedirs('backups')

    # Backup existing files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if os.path.exists('app.py'):
        backup_name = f'backups/app_backup_{timestamp}.py'
        shutil.copy2('app.py', backup_name)
        print(f"✅ Backed up app.py to {backup_name}")

    if os.path.exists('requirements.txt'):
        backup_name = f'backups/requirements_backup_{timestamp}.txt'
        shutil.copy2('requirements.txt', backup_name)
        print(f"✅ Backed up requirements.txt to {backup_name}")

    return True


def update_requirements():
    """Add new requirements to requirements.txt"""
    print("\n📝 Updating requirements.txt...")

    new_requirements = """
# === Enhanced SIS System Dependencies ===
# Database
sqlalchemy==2.0.23
aiosqlite==0.19.0

# LLM providers (optional)
openai==1.3.0
anthropic==0.7.0

# Document processing
PyPDF2==3.0.1
python-docx==1.1.0
"""

    # Read existing requirements
    existing = ""
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            existing = f.read()

    # Check if already added
    if 'sqlalchemy' not in existing:
        with open('requirements.txt', 'a') as f:
            f.write(new_requirements)
        print("✅ Added new dependencies to requirements.txt")
        print(
            "⚠️  Please click 'Stop' and 'Run' button to install new packages")
    else:
        print("✅ Dependencies already in requirements.txt")

    return True


def create_database_models():
    """Create database_models.py file"""
    print("\n📂 Creating database_models.py...")

    code = '''# database_models.py
"""Database models for enhanced SIS system"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

# Database setup
DATABASE_URL = "sqlite:///./sis_requirements.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table
requirement_tags = Table('requirement_tags', Base.metadata,
    Column('requirement_id', Integer, ForeignKey('requirements.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    budget = Column(Float)
    timeline_weeks = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    requirements = relationship("Requirement", back_populates="project")
    documents = relationship("Document", back_populates="project")

class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    description = Column(Text)
    pegs_category = Column(String)
    priority = Column(String)
    status = Column(String, default="Draft")
    confidence_score = Column(Float, default=0.8)
    llm_provider = Column(String, default="local")
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="requirements")
    tags = relationship("Tag", secondary=requirement_tags, back_populates="requirements")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    requirements = relationship("Requirement", secondary=requirement_tags, back_populates="tags")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String)
    content = Column(Text)
    extracted_requirements = Column(JSON)
    pegs_analysis = Column(JSON)
    uploaded_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="documents")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    provider = Column(String)
    messages = Column(JSON)
    created_at = Column(DateTime, default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

    with open('database_models.py', 'w') as f:
        f.write(code)

    print("✅ Created database_models.py")
    return True


def create_llm_service():
    """Create llm_service.py file"""
    print("\n📂 Creating llm_service.py...")

    code = '''# llm_service.py
"""LLM service for requirement generation"""

import os
import json
from typing import Dict, List, Any

class LLMService:
    """Lightweight LLM service for Replit"""

    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY", "")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if self.openai_key:
            try:
                import openai
                openai.api_key = self.openai_key
                self.openai_available = True
            except:
                self.openai_available = False
        else:
            self.openai_available = False

    async def generate_requirements(self, prompt: str, provider: str = "local", context: Dict = None) -> Dict:
        """Generate requirements based on prompt"""

        if provider == "openai" and self.openai_available:
            return await self._generate_openai(prompt, context)
        else:
            return self._generate_local(prompt, context)

    async def _generate_openai(self, prompt: str, context: Dict = None) -> Dict:
        """Generate using OpenAI"""
        try:
            import openai

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a requirements engineering expert using PEGS framework."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )

            return self._parse_response(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._generate_local(prompt, context)

    def _generate_local(self, prompt: str, context: Dict = None) -> Dict:
        """Generate using local rules"""
        prompt_lower = prompt.lower()
        requirements = []

        if "authentication" in prompt_lower:
            requirements.append({
                "title": "Multi-Factor Authentication",
                "description": "System shall implement MFA for all user access points",
                "pegs_category": "System",
                "priority": "Critical",
                "confidence": 0.9
            })

        if "compliance" in prompt_lower:
            requirements.append({
                "title": "FERPA Compliance",
                "description": "System shall ensure FERPA compliance for student data",
                "pegs_category": "Environment",
                "priority": "Critical",
                "confidence": 0.95
            })

        if "performance" in prompt_lower:
            requirements.append({
                "title": "Response Time Requirement",
                "description": "System shall maintain <2 second response time",
                "pegs_category": "System",
                "priority": "High",
                "confidence": 0.85
            })

        if not requirements:
            requirements.append({
                "title": f"Requirement: {prompt[:50]}",
                "description": prompt,
                "pegs_category": "System",
                "priority": "Medium",
                "confidence": 0.7
            })

        return {"requirements": requirements, "provider": "local", "count": len(requirements)}

    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response"""
        return {
            "requirements": [{
                "title": "Generated Requirement",
                "description": response,
                "pegs_category": "System",
                "priority": "Medium",
                "confidence": 0.8
            }],
            "provider": "openai"
        }
'''

    with open('llm_service.py', 'w') as f:
        f.write(code)

    print("✅ Created llm_service.py")
    return True


def create_pegs_classifier():
    """Create pegs_classifier.py file"""
    print("\n📂 Creating pegs_classifier.py...")

    code = '''# pegs_classifier.py
"""PEGS Framework classifier"""

class PEGSClassifier:
    """Classify requirements into PEGS categories"""

    def __init__(self):
        self.keywords = {
            "Project": ["timeline", "schedule", "milestone", "budget", "resource", "deadline"],
            "Environment": ["compliance", "regulation", "integration", "ferpa", "gdpr", "policy"],
            "Goals": ["objective", "target", "metric", "kpi", "roi", "efficiency"],
            "System": ["architecture", "database", "api", "security", "performance", "authentication"]
        }

    def classify(self, text: str) -> dict:
        """Classify text into PEGS categories"""
        scores = {}
        text_lower = text.lower()

        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score / len(keywords) if keywords else 0

        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            scores = {"System": 1.0}

        return scores

    def get_primary_category(self, text: str) -> str:
        """Get primary PEGS category"""
        scores = self.classify(text)
        return max(scores, key=scores.get)
'''

    with open('pegs_classifier.py', 'w') as f:
        f.write(code)

    print("✅ Created pegs_classifier.py")
    return True


def create_app_additions():
    """Create a file with code to add to app.py"""
    print("\n📂 Creating app_additions.py with code to add...")

    code = '''# app_additions.py
"""
INSTRUCTIONS:
1. Copy the imports section to the TOP of your app.py
2. Copy the endpoints section AFTER your existing endpoints
3. Don't remove any of your existing code!
"""

# ========== SECTION 1: ADD THESE IMPORTS TO TOP OF app.py ==========
IMPORTS_TO_ADD = """
# Enhanced SIS System Imports
from database_models import (
    Base, engine, SessionLocal, get_db,
    Project, Requirement, Document, ChatSession, Tag
)
from llm_service import LLMService
from pegs_classifier import PEGSClassifier
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import re
import os

# Initialize services
llm_service = LLMService()
pegs_classifier = PEGSClassifier()

# Initialize database
def init_database():
    db = SessionLocal()
    if not db.query(Project).first():
        default_project = Project(
            name="Student Information System",
            description="SIS with PEGS framework",
            budget=2500000,
            timeline_weeks=29
        )
        db.add(default_project)
        db.commit()
        print("✅ Default project created")
    db.close()

init_database()
"""

# ========== SECTION 2: ADD THESE ENDPOINTS TO YOUR app.py ==========
ENDPOINTS_TO_ADD = """
# Enhanced API Endpoints

@app.post("/api/requirements/generate")
async def generate_requirements(chat_data: dict, db: Session = Depends(get_db)):
    message = chat_data.get("message", "")
    provider = chat_data.get("provider", "local")

    result = await llm_service.generate_requirements(message, provider)

    project = db.query(Project).first()
    for req in result.get("requirements", []):
        db_req = Requirement(
            project_id=project.id if project else 1,
            title=req.get("title", ""),
            description=req.get("description", ""),
            pegs_category=req.get("pegs_category", "System"),
            priority=req.get("priority", "Medium"),
            status="Draft",
            confidence_score=req.get("confidence", 0.8),
            llm_provider=provider
        )
        db.add(db_req)
    db.commit()

    return result

@app.get("/api/requirements")
def get_requirements(pegs_category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Requirement)
    if pegs_category:
        query = query.filter(Requirement.pegs_category == pegs_category)
    requirements = query.all()

    return {
        "count": len(requirements),
        "requirements": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "pegs_category": r.pegs_category,
                "priority": r.priority,
                "status": r.status
            }
            for r in requirements
        ]
    }

@app.get("/api/pegs/stats")
def get_pegs_statistics(db: Session = Depends(get_db)):
    requirements = db.query(Requirement).all()

    stats = {"total": len(requirements), "by_category": {}, "by_priority": {}}

    for req in requirements:
        if req.pegs_category not in stats["by_category"]:
            stats["by_category"][req.pegs_category] = 0
        stats["by_category"][req.pegs_category] += 1

        if req.priority not in stats["by_priority"]:
            stats["by_priority"][req.priority] = 0
        stats["by_priority"][req.priority] += 1

    return stats

@app.get("/api/system/health")
def system_health_check(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "database": "connected",
        "total_requirements": db.query(Requirement).count(),
        "total_projects": db.query(Project).count(),
        "llm_providers": {
            "local": "available",
            "openai": "configured" if os.environ.get("OPENAI_API_KEY") else "not configured"
        }
    }
"""

print("=" * 60)
print("INSTRUCTIONS FOR INTEGRATING INTO app.py:")
print("=" * 60)
print("1. Open your app.py file")
print("2. Add the IMPORTS section to the TOP of app.py")
print("3. Add the ENDPOINTS section AFTER your existing endpoints")
print("4. Save app.py and click Run")
print("=" * 60)
'''

    with open('app_additions.py', 'w') as f:
        f.write(code)

    print(
        "✅ Created app_additions.py - Open this file for integration instructions"
    )
    return True


def main():
    """Run all setup steps"""
    print("=" * 60)
    print("🚀 ENHANCED SIS SYSTEM SETUP")
    print("=" * 60)

    # Step 1: Backup
    if create_backup():
        print("✅ Step 1: Backups complete")

    # Step 2: Update requirements
    if update_requirements():
        print("✅ Step 2: Requirements updated")

    # Step 3: Create database models
    if create_database_models():
        print("✅ Step 3: Database models created")

    # Step 4: Create LLM service
    if create_llm_service():
        print("✅ Step 4: LLM service created")

    # Step 5: Create PEGS classifier
    if create_pegs_classifier():
        print("✅ Step 5: PEGS classifier created")

    # Step 6: Create integration instructions
    if create_app_additions():
        print("✅ Step 6: Integration instructions created")

    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Click 'Stop' then 'Run' to install new packages")
    print("2. Open 'app_additions.py' for integration instructions")
    print("3. Add the code sections to your app.py")
    print("4. Add API keys in Replit Secrets (optional)")
    print("=" * 60)


if __name__ == "__main__":
    main()

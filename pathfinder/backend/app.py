"""
PathFinder API Server - FastAPI backend.
"""
import sys
import os
from contextlib import asynccontextmanager

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from ml_engine import engine as ml_engine
from learning_paths import (
    generate_learning_path, COURSE_GRAPH, get_career_paths, get_all_domains
)
import database as db


@asynccontextmanager
async def lifespan(application):
    """Load ML engine on startup."""
    try:
        ml_engine.load()
    except Exception as e:
        print(f"[WARNING] ML engine failed to load: {e}")
        print("[WARNING] Recommendations will use keyword-based fallback.")
    yield


app = FastAPI(title="PathFinder API", version="1.0.0", lifespan=lifespan)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





# ---- Models ----
class ProfileCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    experience_level: Optional[str] = "beginner"
    interests: Optional[list] = []
    goals: Optional[str] = ""


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    experience_level: Optional[str] = None
    interests: Optional[list] = None
    goals: Optional[str] = None
    completed_courses: Optional[list] = None


class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    text: Optional[str] = ""
    goal: Optional[str] = ""
    experience_level: Optional[str] = "beginner"
    interests: Optional[list] = []
    top_k: Optional[int] = 10


class LearningPathRequest(BaseModel):
    user_id: Optional[str] = None
    goal: str
    experience_level: Optional[str] = "beginner"
    completed_courses: Optional[list] = []
    interests: Optional[list] = []


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str


class ProgressUpdate(BaseModel):
    user_id: str
    course_name: str
    status: str  # not_started, in_progress, completed
    progress_percent: Optional[int] = 0


# ---- Profile Endpoints ----
@app.post("/api/profile")
async def create_profile(profile: ProfileCreate):
    """Create a new learner profile."""
    user_id = db.create_user(
        name=profile.name,
        email=profile.email,
        experience_level=profile.experience_level,
        interests=profile.interests,
        goals=profile.goals,
    )
    return {"user_id": user_id, "message": "Profile created successfully"}


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    """Get learner profile."""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/api/profile/{user_id}")
async def update_profile(user_id: str, profile: ProfileUpdate):
    """Update learner profile."""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = {k: v for k, v in profile.model_dump().items() if v is not None}
    if updates:
        db.update_user(user_id, **updates)

    return {"message": "Profile updated", "user_id": user_id}


# ---- Recommendation Endpoints ----
@app.post("/api/recommend")
async def get_recommendations(req: RecommendRequest):
    """Get AI-powered course recommendations."""
    # Get user context if available
    excluded = []
    if req.user_id:
        user = db.get_user(req.user_id)
        if user:
            excluded = user.get("completed_courses", [])

    search_text = req.text or req.goal or ""
    if req.interests:
        search_text += " " + " ".join(req.interests)

    if not search_text.strip():
        raise HTTPException(status_code=400, detail="Provide text, goal, or interests")

    try:
        results = ml_engine.recommend_courses(
            search_text, top_k=req.top_k, excluded_courses=excluded
        )
    except Exception:
        # Fallback: keyword-based
        results = _keyword_fallback(search_text, req.top_k)

    return {"recommendations": results, "query": search_text}


def _keyword_fallback(text, top_k=10):
    """Simple keyword-based recommendation fallback."""
    text_lower = text.lower()
    scored = []
    for name, info in COURSE_GRAPH.items():
        score = 0
        name_lower = name.lower()
        for word in text_lower.split():
            if word in name_lower:
                score += 2
            for skill in info.get("skills", []):
                if word in skill:
                    score += 1
        if score > 0:
            scored.append({
                "course": name,
                "score": score / 10,
                "explanation": f"Matches your interest in topics related to {name}.",
                "domain": info.get("domain", "General"),
                "difficulty": {1: "Beginner", 2: "Intermediate", 3: "Advanced"}.get(
                    info.get("difficulty", 2), "Intermediate"
                ),
                "keywords": info.get("skills", [])[:5],
            })
    scored.sort(key=lambda x: -x["score"])
    return scored[:top_k]


# ---- Learning Path Endpoints ----
@app.post("/api/learning-path")
async def create_learning_path(req: LearningPathRequest):
    """Generate a personalized learning path."""
    completed = req.completed_courses or []

    if req.user_id:
        user = db.get_user(req.user_id)
        if user:
            completed = user.get("completed_courses", [])

    path = generate_learning_path(
        goal=req.goal,
        completed_courses=completed,
        experience_level=req.experience_level,
        interests=req.interests,
        ml_engine=ml_engine if ml_engine._loaded else None,
    )

    # Save path to user profile
    if req.user_id:
        db.update_user(req.user_id, current_path=path, goals=req.goal)

    return path


@app.get("/api/career-paths")
async def list_career_paths():
    """List all pre-defined career paths."""
    return {"career_paths": get_career_paths()}


# ---- Course Endpoints ----
@app.get("/api/courses")
async def list_courses(domain: Optional[str] = None, difficulty: Optional[str] = None):
    """List all available courses."""
    courses = []
    diff_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

    for name, info in COURSE_GRAPH.items():
        course = {
            "name": name,
            "domain": info.get("domain", "General"),
            "difficulty": {1: "Beginner", 2: "Intermediate", 3: "Advanced"}.get(
                info.get("difficulty", 2), "Intermediate"
            ),
            "duration_hours": info.get("duration_hours", 20),
            "description": info.get("description", ""),
            "skills": info.get("skills", []),
            "prerequisites": info.get("prerequisites", []),
        }

        if domain and course["domain"] != domain:
            continue
        if difficulty and course["difficulty"] != difficulty:
            continue

        courses.append(course)

    courses.sort(key=lambda x: x["name"])
    return {"courses": courses, "total": len(courses), "domains": get_all_domains()}


@app.get("/api/courses/{course_name}")
async def get_course(course_name: str):
    """Get detailed course information."""
    # URL decode
    course_name = course_name.replace("%20", " ")
    info = COURSE_GRAPH.get(course_name)
    if not info:
        raise HTTPException(status_code=404, detail="Course not found")

    result = {"name": course_name, **info}
    result["difficulty"] = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}.get(
        info.get("difficulty", 2), "Intermediate"
    )

    # Add ML-powered insights if available
    if ml_engine._loaded:
        ml_info = ml_engine.get_course_info(course_name)
        if ml_info:
            result["keywords"] = ml_info.get("keywords", [])
            result["num_reviews"] = ml_info.get("num_reviews", 0)
            result["sample_reviews"] = ml_info.get("sample_reviews", [])

    return result


# ---- Chat Endpoints ----
@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Chat with the AI learning assistant."""
    # Save user message
    if req.user_id:
        db.add_chat_message(req.user_id, "user", req.message)

    # Get AI response
    try:
        response = ml_engine.answer_question(req.message)
    except Exception:
        response = {
            "type": "fallback",
            "response": (
                "I'd love to help you with your learning journey! "
                "Tell me about your career goals or what skills you'd like to develop."
            ),
        }

    # Save AI response
    if req.user_id:
        db.add_chat_message(req.user_id, "assistant", response["response"],
                           metadata=response)

    return response


@app.get("/api/chat/{user_id}/history")
async def get_chat_history(user_id: str, limit: int = 50):
    """Get chat history for a user."""
    history = db.get_chat_history(user_id, limit)
    return {"history": history}


# ---- Progress Endpoints ----
@app.post("/api/progress")
async def update_progress(req: ProgressUpdate):
    """Update course progress."""
    db.update_progress(req.user_id, req.course_name, req.status, req.progress_percent)
    return {"message": "Progress updated"}


@app.get("/api/progress/{user_id}")
async def get_progress(user_id: str):
    """Get all progress for a user."""
    progress = db.get_progress(user_id)
    user = db.get_user(user_id)

    # Compute stats
    completed = len([p for p in progress if p["status"] == "completed"])
    in_progress = len([p for p in progress if p["status"] == "in_progress"])
    total_hours = sum(
        COURSE_GRAPH.get(p["course_name"], {}).get("duration_hours", 0)
        for p in progress if p["status"] == "completed"
    )

    # Skill distribution
    skill_domains = {}
    for p in progress:
        if p["status"] in ("completed", "in_progress"):
            domain = COURSE_GRAPH.get(p["course_name"], {}).get("domain", "General")
            skill_domains[domain] = skill_domains.get(domain, 0) + 1

    return {
        "progress": progress,
        "stats": {
            "completed": completed,
            "in_progress": in_progress,
            "total_hours": total_hours,
            "skill_domains": skill_domains,
        },
        "completed_courses": user["completed_courses"] if user else [],
    }


# ---- Health ----
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ml_engine_loaded": ml_engine._loaded,
        "total_courses": len(COURSE_GRAPH),
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)

"""
PathFinder Database - SQLite-based user profile and progress tracking.
"""
import sqlite3
import json
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pathfinder.db")


def get_db():
    """Get database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            experience_level TEXT DEFAULT 'beginner',
            interests TEXT DEFAULT '[]',
            goals TEXT DEFAULT '',
            completed_courses TEXT DEFAULT '[]',
            current_path TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            status TEXT DEFAULT 'not_started',
            progress_percent INTEGER DEFAULT 0,
            started_at TEXT,
            completed_at TEXT,
            notes TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, course_name)
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


def create_user(name, email="", experience_level="beginner", interests=None, goals=""):
    """Create a new user profile."""
    conn = get_db()
    user_id = str(uuid.uuid4())[:8]
    conn.execute(
        "INSERT INTO users (id, name, email, experience_level, interests, goals) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, email, experience_level, json.dumps(interests or []), goals)
    )
    conn.commit()
    conn.close()
    return user_id


def get_user(user_id):
    """Get user profile."""
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        user = dict(row)
        user["interests"] = json.loads(user["interests"])
        user["completed_courses"] = json.loads(user["completed_courses"])
        try:
            user["current_path"] = json.loads(user["current_path"])
        except (json.JSONDecodeError, TypeError):
            user["current_path"] = {}
        return user
    return None


def update_user(user_id, **kwargs):
    """Update user profile fields."""
    conn = get_db()
    for key, value in kwargs.items():
        if key in ("interests", "completed_courses", "current_path"):
            value = json.dumps(value)
        conn.execute(
            f"UPDATE users SET {key} = ?, updated_at = ? WHERE id = ?",
            (value, datetime.now().isoformat(), user_id)
        )
    conn.commit()
    conn.close()


def update_progress(user_id, course_name, status, progress_percent=0):
    """Update course progress."""
    conn = get_db()
    now = datetime.now().isoformat()

    started_at = now if status in ("in_progress", "completed") else None
    completed_at = now if status == "completed" else None

    if progress_percent >= 100:
        status = "completed"
        completed_at = now

    conn.execute("""
        INSERT INTO progress (user_id, course_name, status, progress_percent, started_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, course_name) DO UPDATE SET
            status = excluded.status,
            progress_percent = excluded.progress_percent,
            started_at = COALESCE(progress.started_at, excluded.started_at),
            completed_at = excluded.completed_at
    """, (user_id, course_name, status, progress_percent, started_at, completed_at))
    conn.commit()

    # Update completed_courses in user profile
    if status == "completed":
        user = get_user(user_id)
        if user:
            completed = user["completed_courses"]
            if course_name not in completed:
                completed.append(course_name)
                update_user(user_id, completed_courses=completed)

    conn.close()


def get_progress(user_id):
    """Get all progress for a user."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM progress WHERE user_id = ? ORDER BY started_at", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_chat_message(user_id, role, message, metadata=None):
    """Add a chat message."""
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_history (user_id, role, message, metadata) VALUES (?, ?, ?, ?)",
        (user_id, role, message, json.dumps(metadata or {}))
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=50):
    """Get chat history."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


# Initialize on import
init_db()

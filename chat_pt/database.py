import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

DATABASE_NAME = "chatpt.db"

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration: Add email column if it doesn't exist
    try:
        cursor.execute("SELECT email FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
        conn.commit()

    # Consultations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            workout_plan TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Conversation history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consultation_id) REFERENCES consultations (id)
        )
    """)

    # Exercise progress table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consultation_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            day TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            notes TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (consultation_id) REFERENCES consultations (id)
        )
    """)

    conn.commit()
    conn.close()

def create_user(name: str) -> int:
    """Create a new user and return their ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_users() -> List[Dict[str, Any]]:
    """Get all users."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM users ORDER BY created_at DESC")
    users = [{"id": row[0], "name": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return users

def create_consultation(user_id: int) -> int:
    """Create a new consultation for a user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO consultations (user_id) VALUES (?)", (user_id,))
    consultation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return consultation_id

def save_message(consultation_id: int, role: str, content: str):
    """Save a message to conversation history."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversation_history (consultation_id, role, content) VALUES (?, ?, ?)",
        (consultation_id, role, content)
    )
    conn.commit()
    conn.close()

def get_conversation_history(consultation_id: int) -> List[Dict[str, str]]:
    """Get conversation history for a consultation."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM conversation_history WHERE consultation_id = ? ORDER BY timestamp",
        (consultation_id,)
    )
    messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    conn.close()
    return messages

def save_workout_plan(consultation_id: int, workout_plan: Dict[str, Any]):
    """Save the workout plan JSON to the consultation."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE consultations SET workout_plan = ?, completed = TRUE WHERE id = ?",
        (json.dumps(workout_plan), consultation_id)
    )
    conn.commit()
    conn.close()

def get_workout_plan(consultation_id: int) -> Optional[Dict[str, Any]]:
    """Get the workout plan for a consultation."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT workout_plan FROM consultations WHERE id = ?", (consultation_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None

def get_user_consultations(user_id: int) -> List[Dict[str, Any]]:
    """Get all consultations for a user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, created_at, completed FROM consultations WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    consultations = [
        {"id": row[0], "created_at": row[1], "completed": bool(row[2])}
        for row in cursor.fetchall()
    ]
    conn.close()
    return consultations

def save_exercise_progress(
    user_id: int,
    consultation_id: int,
    exercise_name: str,
    day: str,
    sets: int,
    reps: int,
    weight: float,
    notes: str = ""
):
    """Save exercise progress for a user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO exercise_progress
        (user_id, consultation_id, exercise_name, day, sets, reps, weight, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, consultation_id, exercise_name, day, sets, reps, weight, notes)
    )
    conn.commit()
    conn.close()

def get_exercise_progress(user_id: int, exercise_name: str) -> List[Dict[str, Any]]:
    """Get all progress records for a specific exercise."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT sets, reps, weight, notes, completed_at, day
        FROM exercise_progress
        WHERE user_id = ? AND exercise_name = ?
        ORDER BY completed_at DESC""",
        (user_id, exercise_name)
    )
    progress = [
        {
            "sets": row[0],
            "reps": row[1],
            "weight": row[2],
            "notes": row[3],
            "completed_at": row[4],
            "day": row[5]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return progress

def get_or_create_user_by_email(email: str, name: str) -> int:
    """Get existing user by email or create a new one."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Try to find existing user by email
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        # Create new user with email
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        user_id = cursor.lastrowid
        conn.commit()

    conn.close()
    return user_id

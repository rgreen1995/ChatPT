import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import hashlib
import secrets

DATABASE_NAME = "chatpt.db"

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)

    # Combine password and salt, then hash
    password_salt = (password + salt).encode('utf-8')
    hashed = hashlib.sha256(password_salt).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify a password against a hash."""
    test_hash, _ = hash_password(password, salt)
    return test_hash == hashed_password

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
            password_hash TEXT,
            password_salt TEXT,
            auth_provider TEXT DEFAULT 'email',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrations: Add columns if they don't exist
    try:
        cursor.execute("SELECT email FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT UNIQUE")
        conn.commit()

    try:
        cursor.execute("SELECT password_hash FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN password_salt TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'email'")
        conn.commit()

    # Consultations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            workout_plan TEXT,
            consultation_type TEXT DEFAULT 'training',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Migration: Add consultation_type column if it doesn't exist
    try:
        cursor.execute("SELECT consultation_type FROM consultations LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE consultations ADD COLUMN consultation_type TEXT DEFAULT 'training'")
        # Update all existing consultations to be 'training' type
        cursor.execute("UPDATE consultations SET consultation_type = 'training' WHERE consultation_type IS NULL")
        conn.commit()

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

    # Exercise library table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercise_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            primary_muscles TEXT NOT NULL,
            secondary_muscles TEXT,
            equipment TEXT,
            difficulty TEXT,
            youtube_url TEXT,
            instructions TEXT,
            form_cues TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Missing exercise requests table - track exercises not in library
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missing_exercise_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            user_id INTEGER,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            request_count INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_missing_exercise_name
        ON missing_exercise_requests(exercise_name)
    """)

    # User coaching profile table - shared across training and nutrition
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_coaching_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            profile_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # User coaching memory table - shared coaching memory summary
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_coaching_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            memory_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Nutrition plans table - separate storage for nutrition plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nutrition_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consultation_id INTEGER NOT NULL,
            plan_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (consultation_id) REFERENCES consultations (id)
        )
    """)

    # Create indexes for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_consultation_type
        ON consultations(consultation_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_consultations
        ON consultations(user_id, created_at)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nutrition_plans_user
        ON nutrition_plans(user_id, created_at)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nutrition_plans_consultation
        ON nutrition_plans(consultation_id)
    """)

    conn.commit()
    conn.close()

def create_user(name: str, email: str = None, password: str = None, auth_provider: str = 'email') -> int:
    """Create a new user and return their ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    if password:
        # Hash the password
        hashed_password, salt = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, password_salt, auth_provider) VALUES (?, ?, ?, ?, ?)",
            (name, email, hashed_password, salt, auth_provider)
        )
    else:
        # Legacy support for users without passwords
        cursor.execute(
            "INSERT INTO users (name, email, auth_provider) VALUES (?, ?, ?)",
            (name, email, auth_provider)
        )

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by email and password. Returns user dict or None."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, password_hash, password_salt FROM users WHERE email = ?",
        (email,)
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    user_id, name, email, password_hash, password_salt = result

    # Check if user has a password set
    if not password_hash or not password_salt:
        return None

    # Verify password
    if verify_password(password, password_hash, password_salt):
        return {"id": user_id, "name": name, "email": email}

    return None

def user_exists(email: str) -> bool:
    """Check if a user with this email already exists."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_users() -> List[Dict[str, Any]]:
    """Get all users."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM users ORDER BY created_at DESC")
    users = [{"id": row[0], "name": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return users

def create_consultation(user_id: int, consultation_type: str = 'training') -> int:
    """Create a new consultation for a user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO consultations (user_id, consultation_type) VALUES (?, ?)",
        (user_id, consultation_type)
    )
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

def get_or_create_user_by_email(email: str, name: str, auth_provider: str = 'google') -> int:
    """Get existing user by email or create a new one (for OAuth)."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Try to find existing user by email
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
    else:
        # Create new user with email (OAuth users don't have passwords)
        cursor.execute(
            "INSERT INTO users (name, email, auth_provider) VALUES (?, ?, ?)",
            (name, email, auth_provider)
        )
        user_id = cursor.lastrowid
        conn.commit()

    conn.close()
    return user_id


def log_missing_exercise_request(exercise_name: str, user_id: int = None):
    """Log a request for an exercise that's not in the library."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if this exercise has been requested before (by any user)
    cursor.execute(
        "SELECT id, request_count FROM missing_exercise_requests WHERE LOWER(exercise_name) = LOWER(?) LIMIT 1",
        (exercise_name,)
    )
    existing = cursor.fetchone()

    if existing:
        # Increment the request count
        cursor.execute(
            "UPDATE missing_exercise_requests SET request_count = request_count + 1, requested_at = CURRENT_TIMESTAMP WHERE id = ?",
            (existing[0],)
        )
    else:
        # Create new entry
        cursor.execute(
            "INSERT INTO missing_exercise_requests (exercise_name, user_id) VALUES (?, ?)",
            (exercise_name, user_id)
        )

    conn.commit()
    conn.close()

def get_missing_exercise_requests(min_requests: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
    """Get missing exercise requests sorted by request count."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """SELECT exercise_name, request_count, MAX(requested_at) as last_requested
        FROM missing_exercise_requests
        WHERE request_count >= ?
        GROUP BY LOWER(exercise_name)
        ORDER BY request_count DESC, last_requested DESC
        LIMIT ?""",
        (min_requests, limit)
    )

    requests = [
        {
            "exercise_name": row[0],
            "request_count": row[1],
            "last_requested": row[2]
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return requests


# ============================================================================
# Nutrition Consultation Functions
# ============================================================================

def get_coaching_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's coaching profile (shared across training and nutrition)."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT profile_json FROM user_coaching_profile WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None


def save_coaching_profile(user_id: int, profile: Dict[str, Any]):
    """Save/update user's coaching profile."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    profile_json = json.dumps(profile)

    # Try to update existing profile first
    cursor.execute(
        """UPDATE user_coaching_profile
        SET profile_json = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?""",
        (profile_json, user_id)
    )

    # If no rows were updated, insert a new profile
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO user_coaching_profile (user_id, profile_json) VALUES (?, ?)",
            (user_id, profile_json)
        )

    conn.commit()
    conn.close()


def get_coaching_memory(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's coaching memory summary."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT memory_json FROM user_coaching_memory WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None


def save_coaching_memory(user_id: int, memory: Dict[str, Any]):
    """Save/update user's coaching memory summary."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    memory_json = json.dumps(memory)

    # Try to update existing memory first
    cursor.execute(
        """UPDATE user_coaching_memory
        SET memory_json = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?""",
        (memory_json, user_id)
    )

    # If no rows were updated, insert new memory
    if cursor.rowcount == 0:
        cursor.execute(
            "INSERT INTO user_coaching_memory (user_id, memory_json) VALUES (?, ?)",
            (user_id, memory_json)
        )

    conn.commit()
    conn.close()


def save_nutrition_plan(user_id: int, consultation_id: int, plan: Dict[str, Any]):
    """Save nutrition plan for a consultation."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    plan_json = json.dumps(plan)

    # Check if a plan already exists for this consultation
    cursor.execute(
        "SELECT id FROM nutrition_plans WHERE consultation_id = ?",
        (consultation_id,)
    )
    existing = cursor.fetchone()

    if existing:
        # Update existing plan
        cursor.execute(
            """UPDATE nutrition_plans
            SET plan_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE consultation_id = ?""",
            (plan_json, consultation_id)
        )
    else:
        # Deactivate all previous plans for this user
        cursor.execute(
            "UPDATE nutrition_plans SET is_active = FALSE WHERE user_id = ?",
            (user_id,)
        )

        # Insert new plan
        cursor.execute(
            """INSERT INTO nutrition_plans
            (user_id, consultation_id, plan_json, is_active)
            VALUES (?, ?, ?, TRUE)""",
            (user_id, consultation_id, plan_json)
        )

    conn.commit()
    conn.close()


def get_nutrition_plan(consultation_id: int) -> Optional[Dict[str, Any]]:
    """Get nutrition plan by consultation ID."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT plan_json FROM nutrition_plans WHERE consultation_id = ?",
        (consultation_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None


def get_latest_nutrition_plan(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's latest active nutrition plan."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT plan_json FROM nutrition_plans
        WHERE user_id = ? AND is_active = TRUE
        ORDER BY updated_at DESC LIMIT 1""",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return None


def get_consultation_type(consultation_id: int) -> str:
    """Get the type of a consultation (training or nutrition)."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT consultation_type FROM consultations WHERE id = ?",
        (consultation_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0] if result[0] else 'training'
    return 'training'  # Default to training if not found

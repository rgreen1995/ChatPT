"""
Unified database interface for ChatPT.
Automatically uses Supabase if configured, otherwise falls back to SQLite.
"""

from typing import List, Dict, Any, Optional
import streamlit as st

# Import both database handlers
from chat_pt.supabase_db import SupabaseDB, is_supabase_configured
from chat_pt import database as sqlite_db


# Global database instance
_db_instance = None


def get_db():
    """Get the appropriate database handler (Supabase or SQLite)."""
    global _db_instance

    if _db_instance is None:
        if is_supabase_configured():
            try:
                _db_instance = SupabaseDB()
                if 'db_type' not in st.session_state:
                    st.session_state.db_type = 'supabase'
            except Exception as e:
                st.warning(f"⚠️ Supabase connection failed: {str(e)}. Falling back to SQLite.")
                _db_instance = 'sqlite'
                st.session_state.db_type = 'sqlite'
        else:
            _db_instance = 'sqlite'
            if 'db_type' not in st.session_state:
                st.session_state.db_type = 'sqlite'

    return _db_instance


def init_db():
    """Initialize the database."""
    db = get_db()
    if db == 'sqlite':
        sqlite_db.init_db()
    else:
        # For Supabase, print schema instructions
        schema = db.init_db()
        # Schema needs to be run manually in Supabase dashboard


def create_user(name: str, email: str = None, password: str = None, auth_provider: str = 'email') -> Any:
    """Create a new user and return their ID."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.create_user(name, email, password, auth_provider)
    else:
        return db.create_user(name, email, password, auth_provider)


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by email and password."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.authenticate_user(email, password)
    else:
        return db.authenticate_user(email, password)


def user_exists(email: str) -> bool:
    """Check if a user with this email already exists."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.user_exists(email)
    else:
        return db.user_exists(email)


def get_or_create_user_by_email(email: str, name: str, auth_provider: str = 'google') -> Any:
    """Get existing user by email or create a new one (for OAuth)."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.get_or_create_user_by_email(email, name, auth_provider)
    else:
        return db.get_or_create_user_by_email(email, name, auth_provider)


def create_consultation(user_id: Any) -> Any:
    """Create a new consultation for a user."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.create_consultation(user_id)
    else:
        return db.create_consultation(user_id)


def save_message(consultation_id: Any, role: str, content: str):
    """Save a message to conversation history."""
    db = get_db()
    if db == 'sqlite':
        sqlite_db.save_message(consultation_id, role, content)
    else:
        db.save_message(consultation_id, role, content)


def get_conversation_history(consultation_id: Any) -> List[Dict[str, str]]:
    """Get conversation history for a consultation."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.get_conversation_history(consultation_id)
    else:
        return db.get_conversation_history(consultation_id)


def save_workout_plan(consultation_id: Any, workout_plan: Dict[str, Any]):
    """Save the workout plan JSON to the consultation."""
    db = get_db()
    if db == 'sqlite':
        sqlite_db.save_workout_plan(consultation_id, workout_plan)
    else:
        db.save_workout_plan(consultation_id, workout_plan)


def get_workout_plan(consultation_id: Any) -> Optional[Dict[str, Any]]:
    """Get the workout plan for a consultation."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.get_workout_plan(consultation_id)
    else:
        return db.get_workout_plan(consultation_id)


def get_user_consultations(user_id: Any) -> List[Dict[str, Any]]:
    """Get all consultations for a user."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.get_user_consultations(user_id)
    else:
        return db.get_user_consultations(user_id)


def save_exercise_progress(
    user_id: Any,
    consultation_id: Any,
    exercise_name: str,
    day: str,
    sets: int,
    reps: int,
    weight: float,
    notes: str = ""
):
    """Save exercise progress for a user."""
    db = get_db()
    if db == 'sqlite':
        sqlite_db.save_exercise_progress(user_id, consultation_id, exercise_name, day, sets, reps, weight, notes)
    else:
        db.save_exercise_progress(user_id, consultation_id, exercise_name, day, sets, reps, weight, notes)


def get_exercise_progress(user_id: Any, exercise_name: str) -> List[Dict[str, Any]]:
    """Get all progress records for a specific exercise."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.get_exercise_progress(user_id, exercise_name)
    else:
        return db.get_exercise_progress(user_id, exercise_name)


def get_users() -> List[Dict[str, Any]]:
    """Get all users (SQLite only for now)."""
    db = get_db()
    if db == 'sqlite':
        return sqlite_db.get_users()
    else:
        # For Supabase, you'd implement this if needed
        return []

import os
import tempfile

import pytest

from chat_pt import database


@pytest.fixture()
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp()
    os.close(fd)

    # Override the DATABASE_NAME in the database module
    original_db_name = database.DATABASE_NAME
    database.DATABASE_NAME = path

    # Initialize the database
    database.init_db()

    yield path

    # Restore original and cleanup
    database.DATABASE_NAME = original_db_name
    if os.path.exists(path):
        os.remove(path)


def test_user_operations(temp_db):
    """Test user creation, existence check, and authentication."""
    # Create user
    user_id = database.create_user("Test User", "test@example.com", "password123")
    assert user_id > 0

    # Check if user exists
    assert database.user_exists("test@example.com") is True
    assert database.user_exists("nonexistent@example.com") is False

    # Authenticate
    user = database.authenticate_user("test@example.com", "password123")
    assert user is not None
    assert user["name"] == "Test User"

    # Wrong password
    assert database.authenticate_user("test@example.com", "wrong") is None


def test_consultation_operations(temp_db):
    """Test consultation creation, message saving, and workout plan saving."""
    user_id = database.create_user("Test User", "test@example.com")

    # Create consultation
    consultation_id = database.create_consultation(user_id)
    assert consultation_id > 0

    # Save message
    database.save_message(consultation_id, "user", "Hello")
    history = database.get_conversation_history(consultation_id)
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"

    # Save workout plan
    plan = {"summary": "Test Plan", "schedule": {}}
    database.save_workout_plan(consultation_id, plan)
    saved_plan = database.get_workout_plan(consultation_id)
    assert saved_plan == plan


def test_exercise_progress(temp_db):
    """Test saving and retrieving exercise progress."""
    user_id = database.create_user("Test User", "test@example.com")
    consultation_id = database.create_consultation(user_id)

    database.save_exercise_progress(user_id, consultation_id, "Squat", "Mon", 3, 10, 100.0, "Easy")

    progress = database.get_exercise_progress(user_id, "Squat")
    assert len(progress) == 1
    # Checking database.py: get_exercise_progress returns sets, reps, weight, notes, completed_at, day.
    assert progress[0]["sets"] == 3
    assert progress[0]["reps"] == 10
    assert progress[0]["weight"] == 100.0
    assert progress[0]["day"] == "Mon"

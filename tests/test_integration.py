import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from chat_pt import database, llm_handler


@pytest.fixture()
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    original_db_name = database.DATABASE_NAME
    database.DATABASE_NAME = path
    database.init_db()
    yield path
    database.DATABASE_NAME = original_db_name
    if os.path.exists(path):
        os.remove(path)


@patch("chat_pt.llm_handler.get_secret")
@patch("chat_pt.llm_handler.genai.GenerativeModel")
def test_full_consultation_flow(mock_gemini, mock_get_secret, temp_db):
    """Test the full consultation flow from user creation to plan generation and saving."""
    mock_get_secret.return_value = "fake_key"
    mock_model = MagicMock()
    mock_gemini.return_value = mock_model

    # Mock LLM response with a valid JSON plan
    mock_response = MagicMock()
    mock_response.text = """
    Sure, here is your plan:
    ```json
    {
      "summary": "Strength Plan",
      "training_days": 3,
      "program_duration_weeks": 4,
      "schedule": {
        "Mon": {
          "focus": "Full Body",
          "exercises": [
            {"name": "Squat", "sequence": "1", "sets": 3, "reps": 10, "rest_seconds": 60}
          ]
        }
      },
      "notes": "Good luck"
    }
    ```
    """
    mock_chat = MagicMock()
    mock_model.start_chat.return_value = mock_chat
    mock_chat.send_message.return_value = mock_response

    # 1. Create User
    user_id = database.create_user("User", "user@example.com")

    # 2. Start Consultation
    consultation_id = database.create_consultation(user_id)
    database.save_message(consultation_id, "user", "I want to get stronger")

    # 3. Get LLM response
    handler = llm_handler.LLMHandler(provider="gemini")
    history = database.get_conversation_history(consultation_id)
    response_text = handler.chat(history)

    # 4. Extract and Save Plan
    plan = handler.extract_workout_plan(response_text)
    assert plan is not None
    assert plan["summary"] == "Strength Plan"

    database.save_workout_plan(consultation_id, plan)
    database.save_message(consultation_id, "assistant", response_text)

    # 5. Verify database state
    saved_plan = database.get_workout_plan(consultation_id)
    assert saved_plan == plan

    final_history = database.get_conversation_history(consultation_id)
    assert len(final_history) == 2
    assert final_history[1]["role"] == "assistant"

from unittest.mock import patch

from chat_pt.context_builder import (
    format_memory_summary,
    format_profile_summary,
    get_nutrition_context_summary,
)


def test_format_profile_summary():
    """Test formatting coaching profile."""
    profile = {
        "daily_calories": {"value": 2000, "label": "Daily Calories"},
        "dietary_restrictions": {"value": ["None"], "label": "Restrictions"},
    }
    summary = format_profile_summary(profile)
    assert "Daily Calories: 2000" in summary
    assert "Restrictions: None" in summary

    assert format_profile_summary(None) == "No profile information available yet."


def test_format_memory_summary():
    """Test formatting coaching memory."""
    memory = {
        "summary": "User likes fish",
        "open_questions": ["What is your age?"],
        "recent_updates": ["Swapped chicken for tofu"],
    }
    summary = format_memory_summary(memory)
    assert "User likes fish" in summary
    assert "Open questions: What is your age?" in summary
    assert "Recent updates: Swapped chicken for tofu" in summary

    assert format_memory_summary(None) == "No coaching memory available yet."


@patch("chat_pt.context_builder.get_user_consultations")
@patch("chat_pt.context_builder.get_consultation_type")
@patch("chat_pt.context_builder.get_nutrition_plan")
def test_get_nutrition_context_summary(mock_get_plan, mock_get_type, mock_get_consultations):
    """Test getting nutrition context summary."""
    mock_get_consultations.return_value = [{"id": 1}]
    mock_get_type.return_value = "nutrition"
    mock_get_plan.return_value = {"summary": "High protein plan"}

    summary = get_nutrition_context_summary(123)
    assert summary == "High protein plan"
    mock_get_plan.assert_called_once_with(1)

    # No consultations
    mock_get_consultations.return_value = []
    assert get_nutrition_context_summary(123) is None

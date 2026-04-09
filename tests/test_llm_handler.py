from unittest.mock import MagicMock, patch

from chat_pt.llm_handler import LLMHandler


@patch("chat_pt.llm_handler.get_secret")
def test_is_json_truncated(mock_get_secret):
    """Test JSON truncation detection."""
    mock_get_secret.return_value = "fake_key"
    handler = LLMHandler(provider="gemini")

    # Not truncated
    assert handler.is_json_truncated('{"key": "value"}') is False
    assert handler.is_json_truncated('{"key": [1, 2, 3]}') is False

    # Truncated
    assert handler.is_json_truncated('{"key": "value"') is True
    assert handler.is_json_truncated('{"key": "value",') is True
    assert handler.is_json_truncated('{"key": ') is True
    assert handler.is_json_truncated('{"key": [1, 2') is True


@patch("chat_pt.llm_handler.get_secret")
def test_extract_workout_plan(mock_get_secret):
    """Test extraction of workout plan from LLM response."""
    mock_get_secret.return_value = "fake_key"
    handler = LLMHandler(provider="openai")

    # Valid JSON in code block
    response = 'Here is your plan: ```json\n{"schedule": {"Mon": "Chest"}}\n```'
    plan = handler.extract_workout_plan(response)
    assert plan == {"schedule": {"Mon": "Chest"}}

    # Valid JSON without code block
    response = 'Plan: {"schedule": {"Tue": "Back"}}'
    plan = handler.extract_workout_plan(response)
    assert plan == {"schedule": {"Tue": "Back"}}

    # Invalid JSON
    response = "No JSON here"
    plan = handler.extract_workout_plan(response)
    assert plan is None


@patch("chat_pt.llm_handler.get_secret")
@patch("chat_pt.llm_handler.OpenAI")
def test_chat_openai(mock_openai, mock_get_secret):
    """Test chat with OpenAI provider."""
    mock_get_secret.return_value = "fake_key"
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello from OpenAI"
    mock_client.chat.completions.create.return_value = mock_response

    handler = LLMHandler(provider="openai")
    response = handler.chat([{"role": "user", "content": "Hi"}])

    assert response == "Hello from OpenAI"
    mock_client.chat.completions.create.assert_called_once()


@patch("chat_pt.llm_handler.get_secret")
@patch("chat_pt.llm_handler.requests.post")
def test_chat_anthropic(mock_post, mock_get_secret):
    """Test chat with Anthropic provider."""
    mock_get_secret.return_value = "fake_key"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": [{"text": "Hello from Anthropic"}]}
    mock_post.return_value = mock_response

    handler = LLMHandler(provider="anthropic")
    response = handler.chat([{"role": "user", "content": "Hi"}])

    assert response == "Hello from Anthropic"
    mock_post.assert_called_once()

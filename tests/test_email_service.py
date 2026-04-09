from unittest.mock import patch

from chat_pt import email_service


@patch("chat_pt.email_service.get_secret")
def test_is_email_configured(mock_get_secret):
    """Test if email is correctly identified as configured or not."""
    mock_get_secret.return_value = "fake_key"
    assert email_service.is_email_configured() is True

    mock_get_secret.return_value = None
    assert email_service.is_email_configured() is False


@patch("chat_pt.email_service.get_secret")
@patch("resend.Emails.send")
def test_send_welcome_email(mock_resend_send, mock_get_secret):
    """Test sending a welcome email."""
    mock_get_secret.side_effect = (
        lambda key, default=None: "fake_val" if key != "RESEND_FROM_EMAIL" else default
    )
    mock_resend_send.return_value = {"id": "123"}

    # We need to ensure resend is imported or mocked
    # email_service.py imports resend inside the function

    success = email_service.send_welcome_email("test@example.com", "Tester")
    assert success is True
    mock_resend_send.assert_called_once()

    # Check if arguments contain our data
    args, kwargs = mock_resend_send.call_args
    params = args[0]
    assert params["to"] == ["test@example.com"]
    assert "Tester" in params["subject"]


@patch("chat_pt.email_service.is_email_configured")
def test_send_email_not_configured(mock_configured):
    """Test sending email when it's not configured."""
    mock_configured.return_value = False
    success = email_service.send_welcome_email("test@example.com", "Tester")
    assert success is False

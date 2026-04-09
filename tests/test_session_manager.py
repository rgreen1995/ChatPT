"""Tests for the session_manager module."""

import time

import pytest

from chat_pt.session_manager import (
    clear_session_cookie,
    create_session_token,
    read_session_cookie_js,
    restore_session_from_token,
    set_session_cookie,
    validate_session_token,
)

SECRET = "test-secret-key"


class TestCreateSessionToken:

    """Tests for create_session_token."""

    def test_creates_token_with_signature(self):
        """Token should contain payload and signature separated by a dot."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)
        assert "." in token

    def test_token_contains_user_data(self):
        """Token payload should contain the user id, name, and email."""
        token = create_session_token(42, "Bob", "bob@example.com", secret_key=SECRET)
        payload = token[: token.rfind(".")]
        assert "42" in payload
        assert "Bob" in payload
        assert "bob@example.com" in payload

    def test_token_with_empty_email(self):
        """Token should handle empty email gracefully."""
        token = create_session_token(1, "Alice", "", secret_key=SECRET)
        result = validate_session_token(token, secret_key=SECRET)
        assert result is not None
        assert result["user_email"] == ""

    def test_token_with_none_email(self):
        """Token should handle None email gracefully."""
        token = create_session_token(1, "Alice", None, secret_key=SECRET)
        result = validate_session_token(token, secret_key=SECRET)
        assert result is not None
        assert result["user_email"] == ""

    def test_custom_duration(self):
        """Token expiry should respect the duration parameter."""
        token = create_session_token(1, "Alice", "a@b.com", secret_key=SECRET, duration=3600)
        result = validate_session_token(token, secret_key=SECRET)
        assert result is not None
        # Expiry should be roughly now + 3600
        assert abs(result["expiry"] - (int(time.time()) + 3600)) < 5


class TestValidateSessionToken:

    """Tests for validate_session_token."""

    def test_valid_token(self):
        """A freshly created token should validate successfully."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)
        result = validate_session_token(token, secret_key=SECRET)
        assert result is not None
        assert result["user_id"] == 1
        assert result["user_name"] == "Alice"
        assert result["user_email"] == "alice@example.com"

    def test_expired_token(self):
        """An expired token should return None."""
        token = create_session_token(
            1, "Alice", "alice@example.com", secret_key=SECRET, duration=-1
        )
        result = validate_session_token(token, secret_key=SECRET)
        assert result is None

    def test_tampered_signature(self):
        """A token with a tampered signature should return None."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)
        # Tamper with the last character of the signature
        tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
        result = validate_session_token(tampered, secret_key=SECRET)
        assert result is None

    def test_tampered_payload(self):
        """A token with a tampered payload should return None."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)
        # Change user_id from 1 to 2
        tampered = "2" + token[1:]
        result = validate_session_token(tampered, secret_key=SECRET)
        assert result is None

    def test_wrong_secret_key(self):
        """A token validated with a different key should return None."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)
        result = validate_session_token(token, secret_key="wrong-key")
        assert result is None

    def test_empty_token(self):
        """An empty token should return None."""
        assert validate_session_token("", secret_key=SECRET) is None

    def test_none_token(self):
        """A None token should return None."""
        assert validate_session_token(None, secret_key=SECRET) is None

    def test_no_dot_token(self):
        """A token without a dot separator should return None."""
        assert validate_session_token("nodothere", secret_key=SECRET) is None

    def test_malformed_payload(self):
        """A token with too few payload parts should return None."""
        # Only two parts instead of four
        import hashlib
        import hmac

        payload = "1:Alice"
        sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        token = f"{payload}.{sig}"
        assert validate_session_token(token, secret_key=SECRET) is None

    def test_non_numeric_expiry(self):
        """A token with a non-numeric expiry should return None."""
        import hashlib
        import hmac

        payload = "1:Alice:alice@example.com:not_a_number"
        sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        token = f"{payload}.{sig}"
        assert validate_session_token(token, secret_key=SECRET) is None

    def test_string_user_id(self):
        """A token with a non-integer user_id (e.g. UUID) should parse as string."""
        token = create_session_token(
            "uuid-abc-123", "Alice", "alice@example.com", secret_key=SECRET
        )
        result = validate_session_token(token, secret_key=SECRET)
        assert result is not None
        assert result["user_id"] == "uuid-abc-123"

    def test_uses_default_secret_key(self):
        """Tokens should work with the default secret key when none is specified."""
        token = create_session_token(1, "Alice", "alice@example.com")
        result = validate_session_token(token)
        assert result is not None
        assert result["user_id"] == 1


class TestSetSessionCookie:

    """Tests for set_session_cookie."""

    def test_returns_html_with_script(self):
        """Should return an HTML string containing a script tag."""
        js = set_session_cookie(1, "Alice", "alice@example.com", secret_key=SECRET)
        assert "<script>" in js
        assert "</script>" in js

    def test_contains_cookie_name(self):
        """The JS should set the correct cookie name."""
        js = set_session_cookie(
            1, "Alice", "alice@example.com", secret_key=SECRET, cookie_name="my_cookie"
        )
        assert "my_cookie=" in js

    def test_contains_max_age(self):
        """The JS should include a max-age directive."""
        js = set_session_cookie(1, "Alice", "alice@example.com", secret_key=SECRET, duration=7200)
        assert "max-age=7200" in js

    def test_contains_valid_token(self):
        """The cookie value should be a valid session token."""
        js = set_session_cookie(1, "Alice", "alice@example.com", secret_key=SECRET)
        # Extract token from the JS: cookie_name=<token>;
        # Find between 'chatpt_session=' and '; path'
        start = js.index("chatpt_session=") + len("chatpt_session=")
        end = js.index("; path")
        token = js[start:end]
        result = validate_session_token(token, secret_key=SECRET)
        assert result is not None
        assert result["user_id"] == 1


class TestClearSessionCookie:

    """Tests for clear_session_cookie."""

    def test_returns_html_with_script(self):
        """Should return an HTML string containing a script tag."""
        js = clear_session_cookie()
        assert "<script>" in js
        assert "</script>" in js

    def test_sets_max_age_zero(self):
        """Should expire the cookie by setting max-age=0."""
        js = clear_session_cookie()
        assert "max-age=0" in js

    def test_uses_correct_cookie_name(self):
        """Should target the specified cookie name."""
        js = clear_session_cookie(cookie_name="custom_session")
        assert "custom_session=" in js


class TestReadSessionCookieJs:

    """Tests for read_session_cookie_js."""

    def test_returns_html_with_script(self):
        """Should return an HTML string containing a script tag."""
        js = read_session_cookie_js()
        assert "<script>" in js
        assert "</script>" in js

    def test_reads_correct_cookie_name(self):
        """The JS should look for the correct cookie name."""
        js = read_session_cookie_js(cookie_name="my_session")
        assert "my_session=" in js

    def test_uses_restore_session_param(self):
        """The JS should redirect with a restore_session query param."""
        js = read_session_cookie_js()
        assert "restore_session" in js


class TestRestoreSessionFromToken:

    """Tests for restore_session_from_token."""

    def test_valid_token_without_validation_fn(self):
        """Should return user data for a valid token without DB check."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)
        result = restore_session_from_token(token, secret_key=SECRET)
        assert result is not None
        assert result["user_id"] == 1
        assert result["user_name"] == "Alice"
        assert result["user_email"] == "alice@example.com"

    def test_valid_token_with_passing_validation(self):
        """Should return DB user data when validation function confirms user exists."""
        token = create_session_token(1, "Alice", "alice@example.com", secret_key=SECRET)

        def mock_get_user(user_id):
            return {"id": user_id, "name": "Alice Updated", "email": "new@example.com"}

        result = restore_session_from_token(
            token, secret_key=SECRET, validate_user_fn=mock_get_user
        )
        assert result is not None
        assert result["user_id"] == 1
        assert result["user_name"] == "Alice Updated"
        assert result["user_email"] == "new@example.com"

    def test_valid_token_with_failing_validation(self):
        """Should return None when validation function says user doesn't exist."""
        token = create_session_token(99, "Deleted", "gone@example.com", secret_key=SECRET)

        def mock_get_user(user_id):
            return None

        result = restore_session_from_token(
            token, secret_key=SECRET, validate_user_fn=mock_get_user
        )
        assert result is None

    def test_expired_token_with_validation(self):
        """Should return None for expired token even with validation function."""
        token = create_session_token(
            1, "Alice", "alice@example.com", secret_key=SECRET, duration=-1
        )

        def mock_get_user(user_id):
            return {"id": user_id, "name": "Alice", "email": "alice@example.com"}

        result = restore_session_from_token(
            token, secret_key=SECRET, validate_user_fn=mock_get_user
        )
        assert result is None

    def test_invalid_token(self):
        """Should return None for an invalid token."""
        result = restore_session_from_token("garbage.token", secret_key=SECRET)
        assert result is None

    def test_none_token(self):
        """Should return None for a None token."""
        result = restore_session_from_token(None, secret_key=SECRET)
        assert result is None


class TestGetUserByIdIntegration:

    """Tests for get_user_by_id in the database layer."""

    @pytest.fixture()
    def temp_db(self):
        """Create a temporary database for testing."""
        import os
        import tempfile

        from chat_pt import database

        fd, path = tempfile.mkstemp()
        os.close(fd)
        original_db_name = database.DATABASE_NAME
        database.DATABASE_NAME = path
        database.init_db()
        yield path
        database.DATABASE_NAME = original_db_name
        if os.path.exists(path):
            os.remove(path)

    def test_get_existing_user(self, temp_db):
        """Should return user dict for an existing user."""
        from chat_pt import database

        user_id = database.create_user("Test User", "test@example.com", "password123")
        result = database.get_user_by_id(user_id)
        assert result is not None
        assert result["id"] == user_id
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"

    def test_get_nonexistent_user(self, temp_db):
        """Should return None for a non-existent user ID."""
        from chat_pt import database

        result = database.get_user_by_id(99999)
        assert result is None

    def test_get_user_without_email(self, temp_db):
        """Should return user with None email when no email was provided."""
        from chat_pt import database

        user_id = database.create_user("No Email User")
        result = database.get_user_by_id(user_id)
        assert result is not None
        assert result["id"] == user_id
        assert result["name"] == "No Email User"
        assert result["email"] is None

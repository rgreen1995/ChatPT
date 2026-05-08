"""
Session manager for persistent authentication across Streamlit reconnections.

Uses HMAC-signed tokens stored in browser cookies to survive WebSocket
disconnects and session state resets that cause unexpected logouts.
"""

import hashlib
import hmac
import os
import time
from typing import Any, Optional

# Default session duration: 90 days (in seconds)
DEFAULT_SESSION_DURATION = 90 * 24 * 60 * 60

# Separator used in the token payload
_TOKEN_SEP = ":"


def _get_secret_key() -> str:
    """
    Get the secret key for signing session tokens.

    Uses CHATPT_SESSION_SECRET env var if set, otherwise falls back
    to a deterministic key derived from the machine. For production,
    always set CHATPT_SESSION_SECRET.
    """
    secret = os.environ.get("CHATPT_SESSION_SECRET")
    if secret:
        return secret
    # Fallback: derive from a fixed string (acceptable for single-server deploys)
    return "chatpt-default-session-key-change-in-production"


def create_session_token(
    user_id: Any,
    user_name: str,
    user_email: str,
    secret_key: Optional[str] = None,
    duration: int = DEFAULT_SESSION_DURATION,
) -> str:
    """
    Create a signed session token encoding user identity and expiry.

    Args:
    ----
        user_id: The user's database ID.
        user_name: The user's display name.
        user_email: The user's email address.
        secret_key: Secret key for HMAC signing. Uses default if None.
        duration: Token validity duration in seconds.

    Returns:
    -------
        A signed token string in the format ``payload.signature``.

    """
    if secret_key is None:
        secret_key = _get_secret_key()

    expiry = int(time.time()) + duration

    # Build payload: user_id:user_name:user_email:expiry
    payload = _TOKEN_SEP.join([str(user_id), str(user_name), str(user_email or ""), str(expiry)])

    signature = hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{payload}.{signature}"


def validate_session_token(
    token: str,
    secret_key: Optional[str] = None,
) -> Optional[dict]:
    """
    Validate a signed session token and return its payload.

    Args:
    ----
        token: The signed token string.
        secret_key: Secret key for HMAC verification. Uses default if None.

    Returns:
    -------
        A dict with ``user_id``, ``user_name``, ``user_email``, and
        ``expiry`` if valid, or ``None`` if invalid/expired.

    """
    if not token or "." not in token:
        return None

    if secret_key is None:
        secret_key = _get_secret_key()

    # Split on the last dot to separate payload from signature
    last_dot = token.rfind(".")
    payload = token[:last_dot]
    signature = token[last_dot + 1 :]

    # Verify signature
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return None

    # Parse payload
    parts = payload.split(_TOKEN_SEP)
    if len(parts) < 4:
        return None

    # Reconstruct: user_id is first, expiry is last, name and email in between
    # user_name or user_email may contain the separator, so we handle carefully:
    # Format is user_id:user_name:user_email:expiry
    user_id_str = parts[0]
    expiry_str = parts[-1]
    # user_name and user_email are everything in between
    # Since email is before expiry and after name, and name is after user_id:
    # parts[1] = user_name, parts[2:-1] joined = user_email (email shouldn't have :, but be safe)
    user_name = parts[1]
    user_email = _TOKEN_SEP.join(parts[2:-1])

    try:
        expiry = int(expiry_str)
    except ValueError:
        return None

    # Check expiry
    if time.time() > expiry:
        return None

    # Try to parse user_id as int, fall back to string (for Supabase UUIDs)
    try:
        user_id: Any = int(user_id_str)
    except ValueError:
        user_id = user_id_str

    return {
        "user_id": user_id,
        "user_name": user_name,
        "user_email": user_email,
        "expiry": expiry,
    }


def set_session_cookie(
    user_id: Any,
    user_name: str,
    user_email: str,
    secret_key: Optional[str] = None,
    duration: int = DEFAULT_SESSION_DURATION,
    cookie_name: str = "chatpt_session",
    current_page: Optional[str] = None,
) -> str:
    """
    Generate JavaScript to set a secure session cookie in the browser.

    Args:
    ----
        user_id: The user's database ID.
        user_name: The user's display name.
        user_email: The user's email address.
        secret_key: Secret key for HMAC signing. Uses default if None.
        duration: Token validity duration in seconds.
        cookie_name: Name of the cookie.
        current_page: Current app page to save in localStorage for restoration.

    Returns:
    -------
        HTML/JS string to inject via ``st.components.v1.html``.

    """
    token = create_session_token(user_id, user_name, user_email, secret_key, duration)
    max_age = duration

    # Use JavaScript to set a cookie on the parent document (escaping for safety)
    escaped_token = token.replace("\\", "\\\\").replace("'", "\\'")
    escaped_name = cookie_name.replace("\\", "\\\\").replace("'", "\\'")

    page_js = ""
    if current_page:
        escaped_page = current_page.replace("\\", "\\\\").replace("'", "\\'")
        # Save as both a cookie (readable server-side via st.context.cookies) and
        # localStorage (client-side fallback).
        page_js = (
            f"rootDoc.cookie = 'chatpt_page={escaped_page}; path=/; max-age={max_age}; SameSite=Lax';"
            f"rootWindow.localStorage.setItem('chatpt_page', '{escaped_page}');"
        )

    js = f"""
    <script>
    try {{
        const rootWindow = (window.parent && window.parent !== window) ? window.parent : window;
        const rootDoc = rootWindow.document;
        rootDoc.cookie = '{escaped_name}={escaped_token}; path=/; max-age={max_age}; SameSite=Lax';
        {page_js}
    }} catch (e) {{}}
    </script>
    """
    return js


def clear_session_cookie(cookie_name: str = "chatpt_session") -> str:
    """
    Generate JavaScript to clear the session cookie from the browser.

    Args:
    ----
        cookie_name: Name of the cookie to clear.

    Returns:
    -------
        HTML/JS string to inject via ``st.components.v1.html``.

    """
    escaped_name = cookie_name.replace("\\", "\\\\").replace("'", "\\'")

    js = f"""
    <script>
    try {{
        const rootDoc = (window.parent && window.parent !== window)
            ? window.parent.document : document;
        rootDoc.cookie = '{escaped_name}=; path=/; max-age=0; SameSite=Lax';
    }} catch (e) {{}}
    </script>
    """
    return js


def read_session_cookie_js(cookie_name: str = "chatpt_session") -> str:
    """
    Generate JavaScript that reads the session cookie and triggers auto-login via query params.

    This JS reads the cookie from the parent document and, if found,
    redirects with ``?restore_session=<token>`` so the Python side can
    validate and restore the session.

    Args:
    ----
        cookie_name: Name of the cookie to read.

    Returns:
    -------
        HTML/JS string to inject via ``st.components.v1.html``.

    """
    escaped_name = cookie_name.replace("\\", "\\\\").replace("'", "\\'")

    js = f"""
    <script>
    try {{
        const rootWindow = (window.parent && window.parent !== window) ? window.parent : window;
        const rootDoc = rootWindow.document;
        const cookies = rootDoc.cookie.split(';');
        let sessionToken = null;

        for (let i = 0; i < cookies.length; i++) {{
            const cookie = cookies[i].trim();
            if (cookie.startsWith('{escaped_name}=')) {{
                sessionToken = cookie.substring('{escaped_name}='.length);
                break;
            }}
        }}

        if (sessionToken) {{
            const urlParams = new URLSearchParams(rootWindow.location.search);
            if (!urlParams.has('restore_session')) {{
                const url = new URL(rootWindow.location);
                url.searchParams.set('restore_session', sessionToken);
                try {{
                    const savedPage = rootWindow.localStorage.getItem('chatpt_page');
                    if (savedPage) url.searchParams.set('restore_page', savedPage);
                }} catch (e) {{}}
                rootWindow.location.href = url.toString();
            }}
        }}
    }} catch (e) {{}}
    </script>
    """
    return js


def restore_session_from_token(
    token: str,
    secret_key: Optional[str] = None,
    validate_user_fn=None,
) -> Optional[dict]:
    """
    Validate token and optionally verify user still exists in the database.

    Args:
    ----
        token: The signed session token.
        secret_key: Secret key for HMAC verification. Uses default if None.
        validate_user_fn: Optional callable that takes a user_id and returns
            a user dict if the user exists, or None. Used for server-side
            validation.

    Returns:
    -------
        A dict with ``user_id``, ``user_name``, and ``user_email`` if
        valid, or ``None`` if invalid/expired/user not found.

    """
    session_data = validate_session_token(token, secret_key)
    if session_data is None:
        return None

    # If a validation function is provided, verify user still exists
    if validate_user_fn is not None:
        user = validate_user_fn(session_data["user_id"])
        if user is None:
            return None
        # Use the DB values as source of truth for name/email
        return {
            "user_id": user["id"],
            "user_name": user.get("name", session_data["user_name"]),
            "user_email": user.get("email", session_data["user_email"]),
        }

    return {
        "user_id": session_data["user_id"],
        "user_name": session_data["user_name"],
        "user_email": session_data["user_email"],
    }

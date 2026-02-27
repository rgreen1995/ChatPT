import os
import json
import tempfile
import streamlit as st
from streamlit_google_auth import Authenticate

def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variables."""
    # Try Streamlit secrets first (preferred method)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, KeyError):
        pass
    # Fall back to environment variables
    return os.getenv(key, default)

def get_google_authenticator():
    """Get Google OAuth authenticator if configured."""
    # Check if using credentials file
    credentials_path = get_secret("GOOGLE_CREDENTIALS_PATH")
    if credentials_path and os.path.exists(credentials_path):
        authenticator = Authenticate(
            secret_credentials_path=credentials_path,
            cookie_name='chatpt_auth_cookie',
            cookie_key=get_secret("COOKIE_SECRET_KEY", "default_secret_key_change_me"),
            redirect_uri=get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
        )
        return authenticator

    # Otherwise, check for secrets and create credentials dynamically
    client_id = get_secret("GOOGLE_CLIENT_ID")
    client_secret = get_secret("GOOGLE_CLIENT_SECRET")

    if not (client_id and client_secret):
        return None

    # Create credentials JSON in memory
    credentials = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8501")]
        }
    }

    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(credentials, f)
        temp_path = f.name

    authenticator = Authenticate(
        secret_credentials_path=temp_path,
        cookie_name='chatpt_auth_cookie',
        cookie_key=get_secret("COOKIE_SECRET_KEY", "default_secret_key_change_me"),
        redirect_uri=get_secret("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
    )
    return authenticator

def is_google_auth_configured():
    """Check if Google OAuth is properly configured."""
    credentials_path = get_secret("GOOGLE_CREDENTIALS_PATH")
    if credentials_path and os.path.exists(credentials_path):
        return True

    client_id = get_secret("GOOGLE_CLIENT_ID")
    client_secret = get_secret("GOOGLE_CLIENT_SECRET")
    return bool(client_id and client_secret)

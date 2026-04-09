import streamlit as st

from chat_pt.db_interface import (
    authenticate_user,
    create_user,
    get_user_by_id,
    get_user_consultations,
    init_db,
    user_exists,
)
from chat_pt.session_manager import (
    clear_session_cookie,
    read_session_cookie_js,
    restore_session_from_token,
    set_session_cookie,
)

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="ChatPT - AI Personal Trainer",
    page_icon="💪",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed",  # Collapsed by default on mobile
    menu_items={"About": "ChatPT - Your AI-Powered Personal Trainer"},
)

# Auto-close sidebar on navigation and add smooth transitions
st.markdown(
    """
<script>
// Auto-close sidebar when any button is clicked
document.addEventListener('DOMContentLoaded', function() {
    const closeSidebar = () => {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar && !sidebar.classList.contains('collapsed')) {
            const closeButton = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (closeButton) {
                closeButton.click();
            }
        }
    };
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', closeSidebar);
    });
});
</script>

<style>
/* Smooth transitions for all interactive elements */
button, .stButton button {
    transition: all 0.2s ease-in-out !important;
}

button:hover, .stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}

button:active, .stButton button:active {
    transform: translateY(0px) !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

/* Smooth sidebar transitions */
[data-testid="stSidebar"] {
    transition: all 0.3s ease-in-out !important;
}

[data-testid="stSidebar"][aria-expanded="true"] {
    box-shadow: 2px 0 8px rgba(0,0,0,0.1);
}

/* Smooth page transitions */
.main .block-container {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Smooth form transitions */
.stForm {
    transition: all 0.2s ease-in-out;
}

/* Input field improvements */
input[type="text"], input[type="email"], input[type="password"], textarea {
    transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out !important;
}

input[type="text"]:focus, input[type="email"]:focus, input[type="password"]:focus, textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 1px #667eea !important;
}

/* Better mobile tap targets */
@media (max-width: 768px) {
    button, .stButton button {
        min-height: 44px !important;
        padding: 0.75rem 1rem !important;
    }

    /* Larger touch targets for forms */
    input, textarea, select {
        min-height: 44px !important;
        font-size: 16px !important; /* Prevents iOS zoom on focus */
    }
}

/* Loading spinner smoothness */
.stSpinner > div {
    animation: spin 1s cubic-bezier(0.4, 0.0, 0.2, 1) infinite !important;
}

/* Smooth expander transitions */
.streamlit-expanderHeader {
    transition: background-color 0.2s ease-in-out !important;
}

.streamlit-expanderHeader:hover {
    background-color: rgba(0,0,0,0.02) !important;
}

/* Card-like containers with subtle shadows */
div[data-testid="stVerticalBlock"] > div {
    transition: box-shadow 0.2s ease-in-out;
}

/* Smooth scroll behavior */
html {
    scroll-behavior: smooth;
}
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "history" not in st.session_state:
    st.session_state.history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# Auto-track history when page changes
if st.session_state.page != st.session_state.current_page:
    # If we are not currently going back, add the previous page to history
    if not st.session_state.get("going_back", False):
        st.session_state.history.append(st.session_state.current_page)
        # Cap history at 20 pages
        if len(st.session_state.history) > 20:
            st.session_state.history.pop(0)
    st.session_state.current_page = st.session_state.page
    st.session_state.going_back = False
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "anthropic"
if "auth_checked" not in st.session_state:
    st.session_state.auth_checked = False
if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False
if "going_back" not in st.session_state:
    st.session_state.going_back = False


def navigate_to(page):
    """Navigate to a new page and update history."""
    if st.session_state.page != page:
        st.session_state.page = page
        st.session_state.sidebar_state = "collapsed"
        st.rerun()


def go_back():
    """Go back to the previous page in history."""
    if st.session_state.history:
        prev_page = st.session_state.history.pop()
        st.session_state.going_back = True
        st.session_state.page = prev_page
        st.rerun()
    else:
        st.session_state.page = "home"
        st.rerun()


def persist_auth_cookie(user_id: int, user_name: str, user_email: str):
    """Persist auth data in a signed browser cookie for session recovery."""
    js = set_session_cookie(user_id, user_name, user_email)
    st.components.v1.html(js, height=0)


def clear_auth_cookie():
    """Clear persisted auth cookie from the browser."""
    js = clear_session_cookie()
    st.components.v1.html(js, height=0)


def _query_param_scalar(query_params, key, default=None):
    """Return query param as scalar string for compatibility across Streamlit versions."""
    value = query_params.get(key, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value


if st.session_state.get("scroll_to_top"):
    st.components.v1.html(
        """
    <script>
    try {
        window.parent.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    } catch (e) {}
    </script>
    """,
        height=0,
    )
    st.session_state.scroll_to_top = False

# Refresh session cookie while user is logged in (keeps cookie alive during workouts)
if st.session_state.user_id is not None:
    persist_auth_cookie(
        st.session_state.user_id,
        st.session_state.user_name,
        st.session_state.user_email or "",
    )

# Check for stored auth cookie on first load OR if session was lost
if st.session_state.user_id is None:
    # Inject JS that reads the session cookie and redirects with ?restore_session=<token>
    st.components.v1.html(read_session_cookie_js(), height=0)

    # Check query params for cookie-based session restore
    try:
        query_params = st.query_params
        restore_token = _query_param_scalar(query_params, "restore_session")
        if restore_token:
            session_data = restore_session_from_token(
                restore_token, validate_user_fn=get_user_by_id
            )
            if session_data:
                st.session_state.user_id = session_data["user_id"]
                st.session_state.user_name = session_data["user_name"]
                st.session_state.user_email = session_data["user_email"]
                st.session_state.auth_checked = True
                st.session_state.scroll_to_top = True
                # Clear query params
                st.query_params.clear()
                st.rerun()
    except Exception:
        pass

    st.session_state.auth_checked = True

# Sidebar navigation
with st.sidebar:
    st.title("💪 ChatPT")
    st.markdown("---")

    # User selection/creation (only show when NOT logged in)
    if st.session_state.user_id is None:
        st.subheader("Welcome!")

        # Initialize auth mode in session state
        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"

        # Toggle between login and signup
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Login",
                use_container_width=True,
                type="primary" if st.session_state.auth_mode == "login" else "secondary",
            ):
                st.session_state.auth_mode = "login"
                st.rerun()
        with col2:
            if st.button(
                "Sign Up",
                use_container_width=True,
                type="primary" if st.session_state.auth_mode == "signup" else "secondary",
            ):
                st.session_state.auth_mode = "signup"
                st.rerun()

        st.markdown("---")

        if st.session_state.auth_mode == "login":
            # Login form
            st.write("**Login to your account:**")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password")
                    else:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state.user_id = user["id"]
                            st.session_state.user_name = user["name"]
                            st.session_state.user_email = user["email"]
                            persist_auth_cookie(user["id"], user["name"], user["email"])
                            st.session_state.scroll_to_top = True
                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")

        else:
            # Signup form
            st.write("**Create a new account:**")
            with st.form("signup_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                password_confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button(
                    "Create Account", use_container_width=True, type="primary"
                )

                if submitted:
                    # Validation
                    if not name or not email or not password:
                        st.error("Please fill in all fields")
                    elif password != password_confirm:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif user_exists(email):
                        st.error("An account with this email already exists")
                    else:
                        # Create user
                        try:
                            user_id = create_user(name, email, password, auth_provider="email")
                            st.session_state.user_id = user_id
                            st.session_state.user_name = name
                            st.session_state.user_email = email
                            st.session_state.signup_email_status = None
                            st.session_state.scroll_to_top = True

                            persist_auth_cookie(user_id, name, email)

                            # Send welcome email (non-blocking)
                            try:
                                from chat_pt.email_service import (
                                    is_email_configured,
                                    send_welcome_email,
                                )

                                if is_email_configured():
                                    email_sent = send_welcome_email(email, name)
                                    if email_sent:
                                        st.session_state.signup_email_status = "success"
                                    else:
                                        st.session_state.signup_email_status = "failed"
                                else:
                                    st.session_state.signup_email_status = "not_configured"

                            except Exception as email_error:
                                # Don't fail signup if email fails
                                st.session_state.signup_email_status = f"error: {email_error!s}"

                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating account: {e!s}")
    else:
        # User IS logged in
        st.success(f"Logged in as: {st.session_state.user_name}")

        # Show email status if just signed up
        if st.session_state.get("signup_email_status"):
            status = st.session_state.signup_email_status
            if status == "success":
                st.success("✅ Welcome email sent! Check your inbox.")
            elif status == "failed":
                st.error("❌ Email failed to send. Check API key.")
            elif status == "not_configured":
                st.warning("⚠️ Email service not configured")
            elif status.startswith("error:"):
                st.error(f"📧 {status}")
            # Clear the status after showing it
            st.session_state.signup_email_status = None

        # Show database status (helpful for debugging)
        if st.session_state.get("db_type"):
            db_emoji = "☁️" if st.session_state.db_type == "supabase" else "💾"
            st.caption(f"{db_emoji} {st.session_state.db_type.title()}")

        if st.button("Logout"):
            # Clear session cookie
            clear_auth_cookie()

            # Clear all session state
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None
            st.session_state.page = "home"
            # Reset auth mode
            st.session_state.auth_mode = "login"
            st.session_state.skip_google_auth = False
            # Clear Google auth session if it exists
            if "connected" in st.session_state:
                st.session_state.connected = False
            if "user_info" in st.session_state:
                del st.session_state.user_info
            # Clear consultation data
            if "consultation_id" in st.session_state:
                del st.session_state.consultation_id
            if "messages" in st.session_state:
                del st.session_state.messages
            if "workout_plan" in st.session_state:
                del st.session_state.workout_plan
            st.rerun()

        st.markdown("---")

        # LLM Provider Selection
        st.subheader("LLM Provider")
        provider = st.selectbox(
            "Choose AI Model",
            [
                "anthropic",
            ],
            index=[
                "anthropic",
            ].index(st.session_state.llm_provider),
        )
        st.session_state.llm_provider = provider

        provider_info = {
            # "openai": "🤖 GPT-4",
            "anthropic": "🧠 Claude",
            # "gemini": "✨ Gemini"
        }
        st.info(provider_info[provider])

        st.markdown("---")

        # Navigation
        st.subheader("Navigation")
        if st.button("🏠 Home", use_container_width=True):
            navigate_to("home")
        if st.button("💬 New Consultation", use_container_width=True):
            navigate_to("consultation")
        if st.button("📋 My Plans", use_container_width=True):
            navigate_to("plans")
        if st.button("📚 Exercise Library", use_container_width=True):
            navigate_to("exercises")
        if st.button("📊 Progress Tracking", use_container_width=True):
            navigate_to("progress")

# Main content area
if st.session_state.user_id is None:
    # Mobile-friendly tip about sidebar (only show if not already in sidebar)
    st.markdown(
        """
    <div style="background: #f0f2f6; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; text-align: center;">
        <p style="margin: 0; font-size: 0.9rem; color: #666;">
            💡 <strong>Tip:</strong> On mobile? Tap <strong>></strong> in the top-left to access login/signup
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Hero Section
    st.markdown(
        """
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">💪 ChatPT</h1>
        <p style="font-size: 1.5rem; color: #666; margin-bottom: 2rem;">Your AI-Powered Personal Trainer</p>
        <p style="font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">
            Get personalized workout plans tailored to your goals, experience, and lifestyle through an intelligent AI consultation.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Features Grid
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
            <h3 style="margin: 0.5rem 0; color: white;">Custom Plans</h3>
            <p style="margin: 0; font-size: 0.9rem;">Designed specifically for your goals and experience level</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💬</div>
            <h3 style="margin: 0.5rem 0; color: white;">AI Consultation</h3>
            <p style="margin: 0; font-size: 0.9rem;">Chat naturally with AI to build your perfect program</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; color: white; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
            <h3 style="margin: 0.5rem 0; color: white;">Track Progress</h3>
            <p style="margin: 0; font-size: 0.9rem;">Log workouts and visualize your improvements</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # How It Works Section
    st.markdown(
        """
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h2 style="text-align: center; margin-bottom: 2rem;">How It Works</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">1</div>
            <h4>Sign Up</h4>
            <p style="font-size: 0.9rem; color: #666;">Create your free account</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">2</div>
            <h4>Consult AI</h4>
            <p style="font-size: 0.9rem; color: #666;">Share your goals and experience</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">3</div>
            <h4>Get Plan</h4>
            <p style="font-size: 0.9rem; color: #666;">Receive your custom program</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">4</div>
            <h4>Start Training</h4>
            <p style="font-size: 0.9rem; color: #666;">Follow your personalized plan</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Check if user clicked auth button - show form in main area
    if st.session_state.get("show_auth_in_main"):
        st.markdown(
            """
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3>Let's Get Started! 🚀</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Toggle between login and signup - order based on auth_mode
            if st.session_state.auth_mode == "login":
                tab1, tab2 = st.tabs(["Login", "Sign Up"])

                with tab1:
                    # Login form
                    with st.form("main_login_form"):
                        st.markdown("**Login to your account:**")
                        email = st.text_input("Email")
                        password = st.text_input("Password", type="password")
                        submitted = st.form_submit_button(
                            "Login", use_container_width=True, type="primary"
                        )

                        if submitted:
                            if not email or not password:
                                st.error("Please enter both email and password")
                            else:
                                user = authenticate_user(email, password)
                                if user:
                                    st.session_state.user_id = user["id"]
                                    st.session_state.user_name = user["name"]
                                    st.session_state.user_email = user["email"]
                                    st.session_state.show_auth_in_main = False
                                    st.session_state.scroll_to_top = True
                                    persist_auth_cookie(user["id"], user["name"], user["email"])
                                    st.success(f"Welcome back, {user['name']}!")
                                    st.rerun()
                                else:
                                    st.error("Invalid email or password")

                with tab2:
                    # Signup form
                    with st.form("main_signup_form_alt"):
                        st.markdown("**Create your free account:**")
                        name = st.text_input("Name")
                        email = st.text_input("Email")
                        password = st.text_input("Password", type="password")
                        password_confirm = st.text_input("Confirm Password", type="password")
                        submitted = st.form_submit_button(
                            "Create Account", use_container_width=True, type="primary"
                        )

                        if submitted:
                            # Validation
                            if not name or not email or not password:
                                st.error("Please fill in all fields")
                            elif password != password_confirm:
                                st.error("Passwords don't match")
                            elif len(password) < 6:
                                st.error("Password must be at least 6 characters")
                            elif user_exists(email):
                                st.error("An account with this email already exists")
                            else:
                                # Create user
                                try:
                                    user_id = create_user(
                                        name, email, password, auth_provider="email"
                                    )
                                    st.session_state.user_id = user_id
                                    st.session_state.user_name = name
                                    st.session_state.user_email = email
                                    st.session_state.signup_email_status = None
                                    st.session_state.scroll_to_top = True

                                    persist_auth_cookie(user_id, name, email)

                                    # Send welcome email (non-blocking)
                                    try:
                                        from chat_pt.email_service import (
                                            is_email_configured,
                                            send_welcome_email,
                                        )

                                        if is_email_configured():
                                            email_sent = send_welcome_email(email, name)
                                            if email_sent:
                                                st.session_state.signup_email_status = "success"
                                            else:
                                                st.session_state.signup_email_status = "failed"
                                        else:
                                            st.session_state.signup_email_status = "not_configured"

                                    except Exception as email_error:
                                        st.session_state.signup_email_status = (
                                            f"error: {email_error!s}"
                                        )

                                    st.session_state.show_auth_in_main = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating account: {e!s}")
            else:
                tab1, tab2 = st.tabs(["Sign Up", "Login"])

                with tab1:
                    # Signup form
                    with st.form("main_signup_form"):
                        st.markdown("**Create your free account:**")
                        name = st.text_input("Name")
                        email = st.text_input("Email")
                        password = st.text_input("Password", type="password")
                        password_confirm = st.text_input("Confirm Password", type="password")
                        submitted = st.form_submit_button(
                            "Create Account", use_container_width=True, type="primary"
                        )

                        if submitted:
                            # Validation
                            if not name or not email or not password:
                                st.error("Please fill in all fields")
                            elif password != password_confirm:
                                st.error("Passwords don't match")
                            elif len(password) < 6:
                                st.error("Password must be at least 6 characters")
                            elif user_exists(email):
                                st.error("An account with this email already exists")
                            else:
                                # Create user
                                try:
                                    user_id = create_user(
                                        name, email, password, auth_provider="email"
                                    )
                                    st.session_state.user_id = user_id
                                    st.session_state.user_name = name
                                    st.session_state.user_email = email
                                    st.session_state.signup_email_status = None
                                    st.session_state.scroll_to_top = True
                                    persist_auth_cookie(user_id, name, email)

                                    # Send welcome email (non-blocking)
                                    try:
                                        from chat_pt.email_service import (
                                            is_email_configured,
                                            send_welcome_email,
                                        )

                                        if is_email_configured():
                                            email_sent = send_welcome_email(email, name)
                                            if email_sent:
                                                st.session_state.signup_email_status = "success"
                                            else:
                                                st.session_state.signup_email_status = "failed"
                                        else:
                                            st.session_state.signup_email_status = "not_configured"

                                    except Exception as email_error:
                                        st.session_state.signup_email_status = (
                                            f"error: {email_error!s}"
                                        )

                                    st.session_state.show_auth_in_main = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating account: {e!s}")

                with tab2:
                    # Login form
                    with st.form("main_login_form_alt"):
                        st.markdown("**Login to your account:**")
                        email = st.text_input("Email")
                        password = st.text_input("Password", type="password")
                        submitted = st.form_submit_button(
                            "Login", use_container_width=True, type="primary"
                        )

                        if submitted:
                            if not email or not password:
                                st.error("Please enter both email and password")
                            else:
                                user = authenticate_user(email, password)
                                if user:
                                    st.session_state.user_id = user["id"]
                                    st.session_state.user_name = user["name"]
                                    st.session_state.user_email = user["email"]
                                    st.session_state.show_auth_in_main = False
                                    st.session_state.scroll_to_top = True
                                    persist_auth_cookie(user["id"], user["name"], user["email"])
                                    st.success(f"Welcome back, {user['name']}!")
                                    st.rerun()
                                else:
                                    st.error("Invalid email or password")

            if st.button("← Back to Home", key="back_to_home"):
                st.session_state.show_auth_in_main = False
                st.rerun()

    else:
        # CTA Section with prominent buttons
        st.markdown(
            """
        <div style="text-align: center; margin: 3rem 0 1rem 0;">
            <h3 style="margin-bottom: 1rem;">Ready to Transform Your Fitness?</h3>
            <p style="font-size: 1.1rem; color: #666; margin-bottom: 1.5rem;">Get started with your free personalized workout plan</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Prominent auth buttons for mobile
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 1rem;">
                <h4 style="color: white; margin: 0 0 0.5rem 0;">New to ChatPT?</h4>
                <p style="color: rgba(255,255,255,0.9); margin: 0 0 1rem 0; font-size: 0.9rem;">Create your free account in 30 seconds</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button(
                "🚀 Sign Up Free",
                use_container_width=True,
                type="primary",
                key="main_signup",
            ):
                st.session_state.auth_mode = "signup"
                st.session_state.show_auth_in_main = True
                st.rerun()

            st.markdown(
                "<div style='text-align: center; margin: 1rem 0;'><p style='color: #666;'>Already have an account?</p></div>",
                unsafe_allow_html=True,
            )

            if st.button("Login", use_container_width=True, key="main_login"):
                st.session_state.auth_mode = "login"
                st.session_state.show_auth_in_main = True
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Install as App Section
    with st.expander("📱 Install ChatPT as an App on Your Phone"):
        st.markdown(
            """
        ### iPhone (Safari)
        1. Open ChatPT in **Safari** browser
        2. Tap the **Share** button (square with arrow pointing up) at the bottom
        3. Scroll down and tap **"Add to Home Screen"**
        4. Customize the name if you want, then tap **"Add"**
        5. ChatPT will now appear as an app icon on your home screen!

        ### Android (Chrome)
        1. Open ChatPT in **Chrome** browser
        2. Tap the **three dots** menu (⋮) in the top right
        3. Tap **"Add to Home screen"** or **"Install app"**
        4. Customize the name if you want, then tap **"Add"**
        5. ChatPT will now appear as an app icon on your home screen!

        **Benefits of installing as an app:**
        - 🚀 Faster access from your home screen
        - 📱 Full-screen experience without browser UI
        - 💾 Works offline (for previously loaded pages)
        - 🔔 Better notifications support
        """
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

else:
    # User IS logged in
    # Show a back button for sub-pages to help navigation
    if st.session_state.page != "home":
        col_back, _ = st.columns([1, 3])
        with col_back:
            if st.button("← Back", key="top_back_btn", use_container_width=True):
                # Handle nested navigation for exercise library
                if st.session_state.page == "exercises" and st.session_state.get(
                    "viewing_exercise"
                ):
                    del st.session_state.viewing_exercise
                    st.rerun()
                else:
                    go_back()
        st.markdown("---")

    if st.session_state.page == "home":
        # Hero welcome section
        st.markdown(
            f"""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">Welcome back, {st.session_state.user_name}! 💪</h1>
            <p style="font-size: 1.1rem; color: #666;">Let's crush your fitness goals today</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Quick Actions - Featured CTAs
        st.markdown(
            """
        <div style="margin: 2rem 0 1rem 0;">
            <h3 style="margin-bottom: 1rem;">🚀 Quick Actions</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button(
                "💬 New\nConsultation",
                use_container_width=True,
                type="primary",
                key="home_new_consult",
            ):
                navigate_to("consultation")

        with col2:
            if st.button("📋 My\nPlans", use_container_width=True, key="home_plans"):
                navigate_to("plans")

        with col3:
            if st.button("📚 Exercise\nLibrary", use_container_width=True, key="home_exercises"):
                navigate_to("exercises")

        with col4:
            if st.button("📊 Track\nProgress", use_container_width=True, key="home_progress"):
                navigate_to("progress")

        st.markdown("<br>", unsafe_allow_html=True)

        # Stats Dashboard
        consultations = get_user_consultations(st.session_state.user_id)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{len(consultations)}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Total Consultations</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            completed = sum(1 for c in consultations if c["completed"])
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{completed}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Completed Plans</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                """
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">🎯</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Stay Consistent</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Recent Activity
        if consultations:
            st.markdown(
                """
            <div style="margin: 2rem 0 1rem 0;">
                <h3>📋 Your Recent Consultations</h3>
            </div>
            """,
                unsafe_allow_html=True,
            )

            for i, consultation in enumerate(consultations[:3]):  # Show last 3
                status_color = "#28a745" if consultation["completed"] else "#ffc107"
                status_text = "✅ Completed" if consultation["completed"] else "⏳ In Progress"

                st.markdown(
                    f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {status_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>Consultation #{i+1}</strong>
                            <span style="margin-left: 1rem; color: {status_color}; font-size: 0.9rem;">{status_text}</span>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
            <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🏋️</div>
                <h3 style="margin-bottom: 0.5rem;">Ready to start your fitness journey?</h3>
                <p style="color: #666; margin-bottom: 1.5rem;">Create your first personalized workout plan by starting a consultation with our AI trainer.</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button(
                    "🚀 Start Your First Consultation",
                    use_container_width=True,
                    type="primary",
                    key="home_first_consult",
                ):
                    navigate_to("consultation")

        st.markdown("<br>", unsafe_allow_html=True)

        # Install as App Section
        with st.expander("📱 Install ChatPT as an App on Your Phone"):
            st.markdown(
                """
            ### iPhone (Safari)
            1. Open ChatPT in **Safari** browser
            2. Tap the **Share** button (square with arrow pointing up) at the bottom
            3. Scroll down and tap **"Add to Home Screen"**
            4. Customize the name if you want, then tap **"Add"**
            5. ChatPT will now appear as an app icon on your home screen!

            ### Android (Chrome)
            1. Open ChatPT in **Chrome** browser
            2. Tap the **three dots** menu (⋮) in the top right
            3. Tap **"Add to Home screen"** or **"Install app"**
            4. Customize the name if you want, then tap **"Add"**
            5. ChatPT will now appear as an app icon on your home screen!

            **Benefits of installing as an app:**
            - 🚀 Faster access from your home screen
            - 📱 Full-screen experience without browser UI
            - 💾 Works offline (for previously loaded pages)
            - 🔔 Better notifications support
            """
            )

        st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.page == "consultation":
        # Import consultation page
        from chat_pt import consultation_page

        consultation_page.render()

    if st.session_state.page == "plans":
        # Import plans page
        from chat_pt import plans_page

        plans_page.render()

    if st.session_state.page == "exercises":
        # Import exercise library page
        from chat_pt import exercise_library_page
        from chat_pt.exercise_data import EXERCISE_LIBRARY

        # Check if viewing a specific exercise
        if st.session_state.get("viewing_exercise"):
            exercise_library_page.render_exercise_detail(
                st.session_state.viewing_exercise, EXERCISE_LIBRARY
            )
        else:
            exercise_library_page.render()

    if st.session_state.page == "progress":
        # Import progress page
        from chat_pt import progress_page

        progress_page.render()

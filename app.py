import streamlit as st
from chat_pt.db_interface import (
    init_db, create_user, create_consultation,
    get_user_consultations, get_or_create_user_by_email,
    authenticate_user, user_exists
)
from chat_pt.llm_handler import LLMHandler

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="ChatPT - AI Personal Trainer",
    page_icon="💪",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed",  # Collapsed by default on mobile
    menu_items={
        'About': "ChatPT - Your AI-Powered Personal Trainer and Nutritionist"
    }
)

# Auto-close sidebar on navigation, add smooth transitions, and handle persistent login
st.markdown("""
<script>
// Auto-close sidebar when any button is clicked
document.addEventListener('DOMContentLoaded', function() {
    // Close sidebar on any navigation
    const closeSidebar = () => {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar && !sidebar.classList.contains('collapsed')) {
            const closeButton = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (closeButton) {
                closeButton.click();
            }
        }
    };

    // Listen for button clicks
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', closeSidebar);
    });

    // Store auth token in localStorage when logging in
    window.storeAuthToken = function(userId, userName, userEmail) {
        const authData = {
            userId: userId,
            userName: userName,
            userEmail: userEmail,
            timestamp: Date.now()
        };
        localStorage.setItem('chatpt_auth', JSON.stringify(authData));
    };

    // Clear auth token on logout
    window.clearAuthToken = function() {
        localStorage.removeItem('chatpt_auth');
    };

    // Get stored auth token
    window.getAuthToken = function() {
        const stored = localStorage.getItem('chatpt_auth');
        if (!stored) return null;

        const authData = JSON.parse(stored);
        const ninetyDays = 90 * 24 * 60 * 60 * 1000;

        // Check if token is still valid (90 days for fitness app - don't want users logged out during workouts)
        if (Date.now() - authData.timestamp > ninetyDays) {
            localStorage.removeItem('chatpt_auth');
            return null;
        }

        return authData;
    };

    // Refresh auth timestamp to keep session alive during workouts
    window.refreshAuthToken = function() {
        const stored = localStorage.getItem('chatpt_auth');
        if (stored) {
            const authData = JSON.parse(stored);
            authData.timestamp = Date.now(); // Update timestamp to extend session
            localStorage.setItem('chatpt_auth', JSON.stringify(authData));
        }
    };
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
""", unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "anthropic"
if "auth_checked" not in st.session_state:
    st.session_state.auth_checked = False

# Add session heartbeat to keep auth alive and restore if lost
# This is crucial for preventing logout during workouts or brief disconnections
if st.session_state.user_id is not None:
    st.markdown("""
    <script>
    // Refresh auth token every 5 minutes to keep session alive
    setInterval(function() {
        if (window.refreshAuthToken) {
            window.refreshAuthToken();
        }
    }, 5 * 60 * 1000); // 5 minutes

    // Also refresh on any page interaction (click, touch, scroll)
    ['click', 'touchstart', 'scroll', 'keypress'].forEach(function(event) {
        document.addEventListener(event, function() {
            if (window.refreshAuthToken) {
                window.refreshAuthToken();
            }
        }, { once: false, passive: true });
    });
    </script>
    """, unsafe_allow_html=True)

# Check for stored auth on first load OR if session was lost (crucial for workout continuity)
if st.session_state.user_id is None:
    # Always check localStorage if not logged in - handles reconnection scenarios
    check_auth_html = """
    <script>
    const authData = window.getAuthToken ? window.getAuthToken() : null;
    if (authData) {
        // Send auth data to Streamlit via query params (simple approach)
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('auto_login')) {
            const url = new URL(window.location);
            url.searchParams.set('auto_login', '1');
            url.searchParams.set('user_id', authData.userId);
            url.searchParams.set('user_name', authData.userName);
            url.searchParams.set('user_email', authData.userEmail || '');
            window.location.href = url.toString();
        }
    }
    </script>
    """
    st.components.v1.html(check_auth_html, height=0)

    # Check query params for auto-login
    try:
        query_params = st.query_params
        if query_params.get('auto_login') == '1':
            user_id = query_params.get('user_id')
            user_name = query_params.get('user_name')
            user_email = query_params.get('user_email', '')

            if user_id and user_name:
                st.session_state.user_id = int(user_id)
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                st.session_state.auth_checked = True
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
        if 'auth_mode' not in st.session_state:
            st.session_state.auth_mode = 'login'

        # Toggle between login and signup
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, type="primary" if st.session_state.auth_mode == 'login' else "secondary"):
                st.session_state.auth_mode = 'login'
                st.rerun()
        with col2:
            if st.button("Sign Up", use_container_width=True, type="primary" if st.session_state.auth_mode == 'signup' else "secondary"):
                st.session_state.auth_mode = 'signup'
                st.rerun()

        st.markdown("---")

        if st.session_state.auth_mode == 'login':
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
                            # Store auth in localStorage
                            st.components.v1.html(f"""
                            <script>
                            if (window.storeAuthToken) {{
                                window.storeAuthToken({user["id"]}, '{user["name"]}', '{user["email"]}');
                            }}
                            </script>
                            """, height=0)
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
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

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
                            user_id = create_user(name, email, password, auth_provider='email')
                            st.session_state.user_id = user_id
                            st.session_state.user_name = name
                            st.session_state.user_email = email
                            st.session_state.signup_email_status = None

                            # Store auth in localStorage
                            st.components.v1.html(f"""
                            <script>
                            if (window.storeAuthToken) {{
                                window.storeAuthToken({user_id}, '{name}', '{email}');
                            }}
                            </script>
                            """, height=0)

                            # Send welcome email (non-blocking)
                            try:
                                from chat_pt.email_service import send_welcome_email, is_email_configured

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
                                st.session_state.signup_email_status = f"error: {str(email_error)}"

                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating account: {str(e)}")
    else:
        # User IS logged in
        st.success(f"Logged in as: {st.session_state.user_name}")

        # Show email status if just signed up
        if st.session_state.get('signup_email_status'):
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
        if st.session_state.get('db_type'):
            db_emoji = "☁️" if st.session_state.db_type == 'supabase' else "💾"
            st.caption(f"{db_emoji} {st.session_state.db_type.title()}")

        if st.button("Logout"):
            # Clear localStorage auth
            st.components.v1.html("""
            <script>
            if (window.clearAuthToken) {
                window.clearAuthToken();
            }
            </script>
            """, height=0)

            # Clear all session state
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None
            st.session_state.page = "home"
            # Reset auth mode
            st.session_state.auth_mode = 'login'
            st.session_state.skip_google_auth = False
            # Clear Google auth session if it exists
            if 'connected' in st.session_state:
                st.session_state.connected = False
            if 'user_info' in st.session_state:
                del st.session_state.user_info
            # Clear consultation data
            if 'consultation_id' in st.session_state:
                del st.session_state.consultation_id
            if 'messages' in st.session_state:
                del st.session_state.messages
            if 'workout_plan' in st.session_state:
                del st.session_state.workout_plan
            st.rerun()

        st.markdown("---")

        # LLM Provider Selection
        st.subheader("LLM Provider")
        provider = st.selectbox(
            "Choose AI Model",
            [ "anthropic", ],
            index=["anthropic",].index(st.session_state.llm_provider)
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
            st.session_state.page = "home"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()
        if st.button("💬 New Consultation", use_container_width=True):
            st.session_state.page = "consultation"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()
        if st.button("📋 My Plans", use_container_width=True):
            st.session_state.page = "plans"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()
        if st.button("📚 Exercise Library", use_container_width=True):
            st.session_state.page = "exercises"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()
        if st.button("📊 Progress Tracking", use_container_width=True):
            st.session_state.page = "progress"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()

# Main content area
if st.session_state.user_id is None:
    # Mobile-friendly tip about sidebar (only show if not already in sidebar)
    st.markdown("""
    <div style="background: #f0f2f6; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; text-align: center;">
        <p style="margin: 0; font-size: 0.9rem; color: #666;">
            💡 <strong>Tip:</strong> On mobile? Tap <strong>></strong> in the top-left to access login/signup
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">💪 ChatPT</h1>
        <p style="font-size: 1.5rem; color: #666; margin-bottom: 2rem;">Your AI-Powered Personal Trainer</p>
        <p style="font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">
            Get personalized workout plans tailored to your goals, experience, and lifestyle through an intelligent AI consultation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Features Grid
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
            <h3 style="margin: 0.5rem 0; color: white;">Custom Plans</h3>
            <p style="margin: 0; font-size: 0.9rem;">Designed specifically for your goals and experience level</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💬</div>
            <h3 style="margin: 0.5rem 0; color: white;">AI Consultation</h3>
            <p style="margin: 0; font-size: 0.9rem;">Chat naturally with AI to build your perfect program</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; color: white; height: 100%;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
            <h3 style="margin: 0.5rem 0; color: white;">Track Progress</h3>
            <p style="margin: 0; font-size: 0.9rem;">Log workouts and visualize your improvements</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # How It Works Section
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h2 style="text-align: center; margin-bottom: 2rem;">How It Works</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">1</div>
            <h4>Sign Up</h4>
            <p style="font-size: 0.9rem; color: #666;">Create your free account</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">2</div>
            <h4>Consult AI</h4>
            <p style="font-size: 0.9rem; color: #666;">Share your goals and experience</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">3</div>
            <h4>Get Plan</h4>
            <p style="font-size: 0.9rem; color: #666;">Receive your custom program</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="text-align: center;">
            <div style="background: #667eea; color: white; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; font-weight: bold;">4</div>
            <h4>Start Training</h4>
            <p style="font-size: 0.9rem; color: #666;">Follow your personalized plan</p>
        </div>
        """, unsafe_allow_html=True)

    # Check if user clicked auth button - show form in main area
    if st.session_state.get('show_auth_in_main'):
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3>Let's Get Started! 🚀</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Toggle between login and signup - order based on auth_mode
            if st.session_state.auth_mode == 'login':
                tab1, tab2 = st.tabs(["Login", "Sign Up"])

                with tab1:
                    # Login form
                    with st.form("main_login_form"):
                        st.markdown("**Login to your account:**")
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
                                    st.session_state.show_auth_in_main = False
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
                        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

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
                                    user_id = create_user(name, email, password, auth_provider='email')
                                    st.session_state.user_id = user_id
                                    st.session_state.user_name = name
                                    st.session_state.user_email = email
                                    st.session_state.signup_email_status = None

                                    # Store auth in localStorage
                                    st.components.v1.html(f"""
                                    <script>
                                    if (window.storeAuthToken) {{
                                        window.storeAuthToken({user_id}, '{name}', '{email}');
                                    }}
                                    </script>
                                    """, height=0)

                                    # Send welcome email (non-blocking)
                                    try:
                                        from chat_pt.email_service import send_welcome_email, is_email_configured

                                        if is_email_configured():
                                            email_sent = send_welcome_email(email, name)
                                            if email_sent:
                                                st.session_state.signup_email_status = "success"
                                            else:
                                                st.session_state.signup_email_status = "failed"
                                        else:
                                            st.session_state.signup_email_status = "not_configured"

                                    except Exception as email_error:
                                        st.session_state.signup_email_status = f"error: {str(email_error)}"

                                    st.session_state.show_auth_in_main = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating account: {str(e)}")
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
                        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

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
                                    user_id = create_user(name, email, password, auth_provider='email')
                                    st.session_state.user_id = user_id
                                    st.session_state.user_name = name
                                    st.session_state.user_email = email
                                    st.session_state.signup_email_status = None

                                    # Send welcome email (non-blocking)
                                    try:
                                        from chat_pt.email_service import send_welcome_email, is_email_configured

                                        if is_email_configured():
                                            email_sent = send_welcome_email(email, name)
                                            if email_sent:
                                                st.session_state.signup_email_status = "success"
                                            else:
                                                st.session_state.signup_email_status = "failed"
                                        else:
                                            st.session_state.signup_email_status = "not_configured"

                                    except Exception as email_error:
                                        st.session_state.signup_email_status = f"error: {str(email_error)}"

                                    st.session_state.show_auth_in_main = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error creating account: {str(e)}")

                with tab2:
                    # Login form
                    with st.form("main_login_form_alt"):
                        st.markdown("**Login to your account:**")
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
                                    st.session_state.show_auth_in_main = False
                                    st.success(f"Welcome back, {user['name']}!")
                                    st.rerun()
                                else:
                                    st.error("Invalid email or password")

            if st.button("← Back to Home", key="back_to_home"):
                st.session_state.show_auth_in_main = False
                st.rerun()

    else:
        # CTA Section with prominent buttons
        st.markdown("""
        <div style="text-align: center; margin: 3rem 0 1rem 0;">
            <h3 style="margin-bottom: 1rem;">Ready to Transform Your Fitness?</h3>
            <p style="font-size: 1.1rem; color: #666; margin-bottom: 1.5rem;">Get started with your free personalized workout plan</p>
        </div>
        """, unsafe_allow_html=True)

        # Prominent auth buttons for mobile
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 1rem;">
                <h4 style="color: white; margin: 0 0 0.5rem 0;">New to ChatPT?</h4>
                <p style="color: rgba(255,255,255,0.9); margin: 0 0 1rem 0; font-size: 0.9rem;">Create your free account in 30 seconds</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Sign Up Free", use_container_width=True, type="primary", key="main_signup"):
                st.session_state.auth_mode = 'signup'
                st.session_state.show_auth_in_main = True
                st.rerun()

            st.markdown("<div style='text-align: center; margin: 1rem 0;'><p style='color: #666;'>Already have an account?</p></div>", unsafe_allow_html=True)

            if st.button("Login", use_container_width=True, key="main_login"):
                st.session_state.auth_mode = 'login'
                st.session_state.show_auth_in_main = True
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Install as App Section
    with st.expander("📱 Install ChatPT as an App on Your Phone"):
        st.markdown("""
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
        """)

    st.markdown("<br><br>", unsafe_allow_html=True)

elif st.session_state.page == "home":
    # Hero welcome section
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">Welcome back, {st.session_state.user_name}! 💪</h1>
        <p style="font-size: 1.1rem; color: #666;">Let's crush your fitness goals today</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Actions - Featured CTAs
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h3 style="margin-bottom: 1rem;">🚀 Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💬 New\nConsultation", use_container_width=True, type="primary", key="home_new_consult"):
            st.session_state.page = "consultation"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()

    with col2:
        if st.button("📋 My\nPlans", use_container_width=True, key="home_plans"):
            st.session_state.page = "plans"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()

    with col3:
        if st.button("📚 Exercise\nLibrary", use_container_width=True, key="home_exercises"):
            st.session_state.page = "exercises"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()

    with col4:
        if st.button("📊 Track\nProgress", use_container_width=True, key="home_progress"):
            st.session_state.page = "progress"
            st.session_state.sidebar_state = "collapsed"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats Dashboard
    consultations = get_user_consultations(st.session_state.user_id)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Total Consultations</div>
        </div>
        """.format(len(consultations)), unsafe_allow_html=True)

    with col2:
        completed = sum(1 for c in consultations if c["completed"])
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Completed Plans</div>
        </div>
        """.format(completed), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">🎯</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Stay Consistent</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Recent Activity
    if consultations:
        st.markdown("""
        <div style="margin: 2rem 0 1rem 0;">
            <h3>📋 Your Recent Consultations</h3>
        </div>
        """, unsafe_allow_html=True)

        for i, consultation in enumerate(consultations[:3]):  # Show last 3
            status_color = "#28a745" if consultation["completed"] else "#ffc107"
            status_text = "✅ Completed" if consultation["completed"] else "⏳ In Progress"

            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {status_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>Consultation #{i+1}</strong>
                        <span style="margin-left: 1rem; color: {status_color}; font-size: 0.9rem;">{status_text}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🏋️</div>
            <h3 style="margin-bottom: 0.5rem;">Ready to start your fitness journey?</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">Create your first personalized workout plan by starting a consultation with our AI trainer.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Your First Consultation", use_container_width=True, type="primary", key="home_first_consult"):
                st.session_state.page = "consultation"
                st.session_state.sidebar_state = "collapsed"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Install as App Section
    with st.expander("📱 Install ChatPT as an App on Your Phone"):
        st.markdown("""
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
        """)

elif st.session_state.page == "consultation":
    # Import consultation page
    from chat_pt import consultation_page
    consultation_page.render()

elif st.session_state.page == "plans":
    # Import plans page
    from chat_pt import plans_page
    plans_page.render()

elif st.session_state.page == "exercises":
    # Import exercise library page
    from chat_pt import exercise_library_page
    from chat_pt.exercise_data import EXERCISE_LIBRARY

    # Check if viewing a specific exercise
    if st.session_state.get('viewing_exercise'):
        exercise_library_page.render_exercise_detail(
            st.session_state.viewing_exercise,
            EXERCISE_LIBRARY
        )
    else:
        exercise_library_page.render()

elif st.session_state.page == "progress":
    # Import progress page
    from chat_pt import progress_page
    progress_page.render()

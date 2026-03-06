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
        'About': "ChatPT - Your AI-Powered Personal Trainer"
    }
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "anthropic"

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

                            # Send welcome email (non-blocking)
                            try:
                                from chat_pt.email_service import send_welcome_email, is_email_configured

                                if is_email_configured():
                                    email_sent = send_welcome_email(email, name)
                                    if email_sent:
                                        st.info("📧 Welcome email sent! Check your inbox.")
                                    else:
                                        st.warning("⚠️ Email service configured but email failed to send.")
                                else:
                                    st.caption("💡 Email service not configured - no welcome email sent")

                            except Exception as email_error:
                                # Don't fail signup if email fails
                                st.warning(f"Email error: {str(email_error)}")

                            st.success(f"Account created! Welcome, {name}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating account: {str(e)}")
    else:
        # User IS logged in
        st.success(f"Logged in as: {st.session_state.user_name}")

        # Show database status (helpful for debugging)
        if st.session_state.get('db_type'):
            db_emoji = "☁️" if st.session_state.db_type == 'supabase' else "💾"
            st.caption(f"{db_emoji} {st.session_state.db_type.title()}")

        if st.button("Logout"):
            # Clear all session state
            st.session_state.user_id = None
            st.session_state.user_name = None
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
            st.rerun()
        if st.button("💬 New Consultation", use_container_width=True):
            st.session_state.page = "consultation"
            st.rerun()
        if st.button("📋 My Plans", use_container_width=True):
            st.session_state.page = "plans"
            st.rerun()
        if st.button("📚 Exercise Library", use_container_width=True):
            st.session_state.page = "exercises"
            st.rerun()
        if st.button("📊 Progress Tracking", use_container_width=True):
            st.session_state.page = "progress"
            st.rerun()

# Main content area
if st.session_state.user_id is None:
    st.title("Welcome to ChatPT 💪")
    st.markdown("""
    ## Your AI-Powered Personal Trainer

    ChatPT creates personalized workout plans tailored to your goals, experience, and lifestyle through an intelligent AI consultation.

    ### What You'll Get:
    - 🎯 **Custom Workout Plan**: Designed specifically for your goals and experience level
    - 💬 **Interactive Consultation**: Chat naturally with AI to build your perfect program
    - 📋 **Detailed Exercise Programs**: Complete with sets, reps, and progression guidance
    - 🔄 **Easy Updates**: Modify your plan anytime by chatting with the AI
    - 📊 **Progress Tracking**: Log workouts and track your improvements over time

    ### How It Works:
    1. **Create an account** using the sidebar 👈
    2. **Tell us about yourself** - fitness goals, experience, available time
    3. **Get your custom plan** - Generated in minutes
    4. **Start training** - Follow your personalized program

    ### Get Started:
    👈 Create an account or login using the sidebar!
    """)

    # Only show setup instructions if this appears to be self-hosted (not on Streamlit Cloud)
    import os
    if os.path.exists('.env') or not os.getenv('STREAMLIT_SHARING_MODE'):
        with st.expander("🔧 Self-Hosting Setup"):
            st.markdown("""
            **For developers running ChatPT locally:**

            Create a `.env` file with your API keys:
            ```
            ANTHROPIC_API_KEY=your-key-here
            ```

            Optional Google OAuth:
            ```
            GOOGLE_CLIENT_ID=your-client-id
            GOOGLE_CLIENT_SECRET=your-secret
            GOOGLE_REDIRECT_URI=http://localhost:8501
            ```
            """)

elif st.session_state.page == "home":
    st.title(f"Welcome back, {st.session_state.user_name}! 💪")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Your Consultations")
        consultations = get_user_consultations(st.session_state.user_id)
        if consultations:
            st.metric("Total Consultations", len(consultations))
            st.metric("Completed Plans", sum(1 for c in consultations if c["completed"]))
        else:
            st.info("No consultations yet. Start your first one!")

    with col2:
        st.subheader("🚀 Quick Actions")
        if st.button("Start New Consultation", use_container_width=True, type="primary"):
            st.session_state.page = "consultation"
            st.rerun()
        if st.button("View My Plans", use_container_width=True):
            st.session_state.page = "plans"
            st.rerun()
        if st.button("Track Progress", use_container_width=True):
            st.session_state.page = "progress"
            st.rerun()

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

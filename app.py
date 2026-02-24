import streamlit as st
from chat_pt.database import init_db, create_user, get_users, create_consultation, get_user_consultations, get_or_create_user_by_email
from chat_pt.llm_handler import LLMHandler
from chat_pt.google_auth import is_google_auth_configured, get_google_authenticator

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

# Google OAuth login (if configured)
google_auth_enabled = is_google_auth_configured()
authenticator = None

if google_auth_enabled:
    try:
        authenticator = get_google_authenticator()
        if authenticator and st.session_state.user_id is None:
            authenticator.check_authentification()
            authenticator.login()

            if st.session_state.get('connected', False):
                user_info = st.session_state.get('user_info', {})
                email = user_info.get('email')
                name = user_info.get('name')

                if email and name:
                    # Create or get user based on Google email
                    user_id = get_or_create_user_by_email(email, name)
                    st.session_state.user_id = user_id
                    st.session_state.user_name = name
                    st.session_state.user_email = email
                    st.rerun()
    except Exception as e:
        st.sidebar.warning(f"Google OAuth error: {e}. Using manual login.")
        google_auth_enabled = False

# Sidebar navigation
with st.sidebar:
    st.title("💪 ChatPT")
    st.markdown("---")

    # User selection/creation
    if st.session_state.user_id is None and not google_auth_enabled:
        st.subheader("Welcome!")
        users = get_users()

        if users:
            user_options = ["Create New User"] + [f"{u['name']} (ID: {u['id']})" for u in users]
            selected = st.selectbox("Select User", user_options)

            if selected != "Create New User":
                selected_user = next(u for u in users if f"{u['name']} (ID: {u['id']})" == selected)
                if st.button("Login"):
                    st.session_state.user_id = selected_user["id"]
                    st.session_state.user_name = selected_user["name"]
                    st.rerun()
            else:
                new_name = st.text_input("Enter your name")
                if st.button("Create Account") and new_name:
                    user_id = create_user(new_name)
                    st.session_state.user_id = user_id
                    st.session_state.user_name = new_name
                    st.rerun()
        else:
            st.write("No users yet. Create your account!")
            new_name = st.text_input("Enter your name")
            if st.button("Create Account") and new_name:
                user_id = create_user(new_name)
                st.session_state.user_id = user_id
                st.session_state.user_name = new_name
                st.rerun()
    else:
        st.success(f"Logged in as: {st.session_state.user_name}")
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.page = "home"
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
        if st.button("📊 Progress Tracking", use_container_width=True):
            st.session_state.page = "progress"
            st.rerun()

# Main content area
if st.session_state.user_id is None:
    st.title("Welcome to ChatPT 💪")
    st.markdown("""
    ## Your AI-Powered Personal Trainer

    ChatPT helps you create personalized workout plans through an intelligent consultation process.

    ### Features:
    - 🤖 **AI Consultation**: Chat with advanced AI models (GPT-4, Claude, or Gemini)
    - 📋 **Custom Plans**: Get tailored workout programs based on your goals
    - 📊 **Progress Tracking**: Log your workouts and track improvements
    - 💾 **Conversation History**: Update your plan based on injuries or changes
    - 🎯 **Multiple LLM Support**: Choose your preferred AI model

    ### Get Started:
    👈 Create an account or login using the sidebar!
    """)

    # API Key setup info
    with st.expander("⚙️ Setup Instructions"):
        st.markdown("""
        ### Required API Keys

        Set up your environment variables for the LLM provider(s) you want to use:

        ```bash
        export OPENAI_API_KEY="your-openai-key"
        export ANTHROPIC_API_KEY="your-anthropic-key"
        export GEMINI_API_KEY="your-gemini-key"
        ```

        ### Google OAuth (Optional)

        To enable Google Sign-In, set these environment variables:

        ```bash
        export GOOGLE_CLIENT_ID="your-google-client-id"
        export GOOGLE_CLIENT_SECRET="your-google-client-secret"
        export GOOGLE_REDIRECT_URI="http://localhost:8501"
        ```

        Get your credentials from [Google Cloud Console](https://console.cloud.google.com/)

        Or create a `.env` file in the project directory.
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

elif st.session_state.page == "progress":
    # Import progress page
    from chat_pt import progress_page
    progress_page.render()

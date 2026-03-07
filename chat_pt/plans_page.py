import streamlit as st
import pandas as pd
from chat_pt.db_interface import get_user_consultations, get_workout_plan, get_conversation_history

def render():
    """Render the workout plans page."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋 My Workout Plans</h1>
        <p style="font-size: 1.1rem; color: #666;">Your personalized training programs</p>
    </div>
    """, unsafe_allow_html=True)

    # Get user's consultations
    consultations = get_user_consultations(st.session_state.user_id)

    if not consultations:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
            <h3 style="margin-bottom: 0.5rem;">No workout plans yet</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">Start a consultation to create your first personalized plan!</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Consultation", type="primary", use_container_width=True):
                st.session_state.page = "consultation"
                st.rerun()
        return

    # Filter completed consultations
    completed_consultations = [c for c in consultations if c["completed"]]

    if not completed_consultations:
        st.markdown("""
        <div style="background: #fff3cd; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #ffc107; margin: 2rem 0;">
            <h4 style="margin: 0 0 0.5rem 0;">⏳ Consultation in Progress</h4>
            <p style="margin: 0; color: #666;">You have consultations in progress but no completed plans yet.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue Consultation", type="primary", use_container_width=True):
            st.session_state.page = "consultation"
            st.rerun()
        return

    # Consultation selector
    st.markdown("""
    <div style="margin: 1rem 0;">
        <h3>Select a Plan</h3>
    </div>
    """, unsafe_allow_html=True)

    consultation_options = [
        f"Plan {c['id']} - Created: {c['created_at']}" for c in completed_consultations
    ]

    selected_idx = st.selectbox(
        "Choose a workout plan to view",
        range(len(consultation_options)),
        format_func=lambda i: consultation_options[i],
        label_visibility="collapsed"
    )

    selected_consultation = completed_consultations[selected_idx]
    consultation_id = selected_consultation["id"]

    # Load workout plan
    workout_plan = get_workout_plan(consultation_id)

    if not workout_plan:
        st.error("Error loading workout plan.")
        return

    st.markdown("<br>", unsafe_allow_html=True)

    # Display plan summary with gradient cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{workout_plan.get("training_days", "N/A")}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Training Days/Week</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{workout_plan.get('program_duration_weeks', 'N/A')}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Program Weeks</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{len(workout_plan.get("schedule", {}))}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Workout Days</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Display summary
    if "summary" in workout_plan:
        st.markdown("""
        <div style="margin: 1rem 0;">
            <h3>📝 Plan Overview</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
            {workout_plan["summary"]}
        </div>
        """, unsafe_allow_html=True)

    # Display workout schedule
    st.subheader("🏋️ Workout Schedule")

    schedule = workout_plan.get("schedule", {})

    # Create tabs for each day
    if schedule:
        day_tabs = st.tabs(list(schedule.keys()))

        for day_tab, (day_name, day_data) in zip(day_tabs, schedule.items()):
            with day_tab:
                st.markdown(f"### {day_data.get('focus', 'Workout')}")

                exercises = day_data.get("exercises", [])

                if exercises:
                    # Display exercises with clickable links to exercise library
                    for idx, exercise in enumerate(exercises, 1):
                        exercise_name = exercise.get("name", "N/A")

                        # Exercise header with info button
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{exercise.get('sequence', idx)}. {exercise_name}**")
                        with col2:
                            if st.button("ℹ️ Info", key=f"{day_name}_{idx}_info", help="View exercise details"):
                                st.session_state.viewing_exercise = exercise_name
                                st.session_state.page = "exercises"
                                st.rerun()

                        # Exercise details
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.caption(f"**Sets:** {exercise.get('sets', 'N/A')}")
                        with col2:
                            st.caption(f"**Reps:** {exercise.get('reps', 'N/A')}")
                        with col3:
                            st.caption(f"**Rest:** {exercise.get('rest_seconds', 'N/A')}s")
                        with col4:
                            pass

                        if exercise.get("notes"):
                            st.caption(f"💡 {exercise['notes']}")

                        st.markdown("---")

                    # Add option to log this workout
                    if st.button(f"📊 Log {day_name} Workout", key=f"log_{day_name}", use_container_width=True):
                        st.session_state.page = "progress"
                        st.session_state.selected_day = day_name
                        st.session_state.selected_consultation = consultation_id
                        st.rerun()
                else:
                    st.warning("No exercises found for this day.")

    # Display additional notes
    if "notes" in workout_plan and workout_plan["notes"]:
        st.subheader("📌 Additional Notes & Guidance")
        st.markdown(workout_plan["notes"])

    # View conversation history
    with st.expander("💬 View Consultation Conversation"):
        messages = get_conversation_history(consultation_id)
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Track Progress", use_container_width=True):
            st.session_state.page = "progress"
            st.session_state.selected_consultation = consultation_id
            st.rerun()

    with col2:
        if st.button("💬 Continue Consultation", use_container_width=True):
            # Resume the consultation with this plan's history
            st.session_state.consultation_id = consultation_id
            st.session_state.messages = get_conversation_history(consultation_id)
            st.session_state.workout_plan = workout_plan
            st.session_state.page = "consultation"
            st.rerun()

    with col3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

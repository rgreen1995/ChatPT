import streamlit as st
import pandas as pd
from chat_pt.database import get_user_consultations, get_workout_plan, get_conversation_history

def render():
    """Render the workout plans page."""
    st.title("📋 My Workout Plans")

    # Get user's consultations
    consultations = get_user_consultations(st.session_state.user_id)

    if not consultations:
        st.info("You don't have any workout plans yet. Start a consultation to create your first plan!")
        if st.button("Start Consultation", type="primary"):
            st.session_state.page = "consultation"
            st.rerun()
        return

    # Filter completed consultations
    completed_consultations = [c for c in consultations if c["completed"]]

    if not completed_consultations:
        st.warning("You have consultations in progress but no completed plans yet.")
        if st.button("Continue Consultation", type="primary"):
            st.session_state.page = "consultation"
            st.rerun()
        return

    # Consultation selector
    st.subheader("Select a Plan")
    consultation_options = [
        f"Plan {c['id']} - Created: {c['created_at']}" for c in completed_consultations
    ]

    selected_idx = st.selectbox(
        "Choose a workout plan to view",
        range(len(consultation_options)),
        format_func=lambda i: consultation_options[i]
    )

    selected_consultation = completed_consultations[selected_idx]
    consultation_id = selected_consultation["id"]

    # Load workout plan
    workout_plan = get_workout_plan(consultation_id)

    if not workout_plan:
        st.error("Error loading workout plan.")
        return

    st.markdown("---")

    # Display plan summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Training Days/Week", workout_plan.get("training_days", "N/A"))
    with col2:
        st.metric("Program Duration", f"{workout_plan.get('program_duration_weeks', 'N/A')} weeks")
    with col3:
        st.metric("Total Workout Days", len(workout_plan.get("schedule", {})))

    # Display summary
    if "summary" in workout_plan:
        st.subheader("📝 Plan Overview")
        st.info(workout_plan["summary"])

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
                    # Create a dataframe for better display
                    exercise_data = []
                    for idx, exercise in enumerate(exercises, 1):
                        exercise_data.append({
                            "#": exercise.get("sequence", "N/A"),
                            "Exercise": exercise.get("name", "N/A"),
                            "Sets": exercise.get("sets", "N/A"),
                            "Reps": exercise.get("reps", "N/A"),
                            "Rest (sec)": exercise.get("rest_seconds", "N/A"),
                            "Notes": exercise.get("notes", "")
                        })

                    df = pd.DataFrame(exercise_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # Add option to log this workout
                    st.markdown("---")
                    if st.button(f"📊 Log {day_name} Workout", key=f"log_{day_name}"):
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

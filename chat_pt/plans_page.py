import streamlit as st
import pandas as pd
from chat_pt.db_interface import get_user_consultations, get_workout_plan, get_conversation_history

def sort_workout_days(schedule_dict):
    """Sort workout days in a sensible order (days of week or numerical)."""
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_abbrev = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    keys = list(schedule_dict.keys())

    # Try to sort by day of week
    def day_sort_key(day_name):
        day_lower = day_name.lower()

        # Check for full day names
        for idx, dow in enumerate(days_of_week):
            if dow in day_lower:
                return (0, idx)  # (priority, day_index)

        # Check for abbreviated day names
        for idx, abbr in enumerate(day_abbrev):
            if abbr in day_lower:
                return (0, idx)

        # Check for "Day X" format
        if 'day' in day_lower:
            import re
            match = re.search(r'day\s*(\d+)', day_lower)
            if match:
                return (1, int(match.group(1)))

        # Check for pure numbers at start
        import re
        match = re.match(r'^(\d+)', day_name)
        if match:
            return (2, int(match.group(1)))

        # Fallback: alphabetical
        return (3, day_name.lower())

    sorted_keys = sorted(keys, key=day_sort_key)
    return {k: schedule_dict[k] for k in sorted_keys}

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

    # Create descriptive names for each plan (short - 3-4 words max)
    consultation_options = []
    for c in completed_consultations:
        plan = get_workout_plan(c['id'])
        if plan:
            # Extract key details
            days = plan.get('training_days')
            weeks = plan.get('program_duration_weeks')
            num_days = len(plan.get('schedule', {}))

            # Build concise name
            if days and weeks:
                plan_name = f"{days}-Day • {weeks}wk"
            elif days:
                plan_name = f"{days}-Day Program"
            elif num_days:
                plan_name = f"{num_days}-Day Program"
            else:
                # Use date as fallback
                import datetime
                try:
                    date_obj = datetime.datetime.fromisoformat(c['created_at'])
                    plan_name = date_obj.strftime("%b %d, %Y")
                except:
                    plan_name = "Workout Plan"

            consultation_options.append(plan_name)
        else:
            consultation_options.append("Workout Plan")

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

    # Exercise swap dialog
    if st.session_state.get('show_swap_dialog'):
        exercise_to_swap = st.session_state.get('swap_exercise')
        swap_day = st.session_state.get('swap_day')

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin: 1rem 0;">
            <h3 style="margin: 0 0 0.5rem 0; color: white;">🔄 Request Exercise Swap</h3>
            <p style="margin: 0; opacity: 0.9;">Swap: <strong>{exercise_to_swap}</strong> on {swap_day}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Why do you need to swap?**")
            swap_reason = st.radio(
                "Reason",
                ["Equipment not available", "Injury/discomfort", "Prefer different exercise", "Other"],
                key="swap_reason",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**Type of change:**")
            change_type = st.radio(
                "Change type",
                ["Just for today (temporary)", "Update my plan (permanent)"],
                key="change_type",
                label_visibility="collapsed"
            )

        additional_info = st.text_area(
            "Additional details (optional)",
            placeholder="E.g., 'knee pain', 'only have dumbbells', 'prefer bodyweight'...",
            key="swap_additional_info"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Request Swap from AI", type="primary", use_container_width=True):
                # Build the swap request message
                is_permanent = "permanent" in change_type.lower()
                request_text = f"I need to swap '{exercise_to_swap}' on {swap_day}. "
                request_text += f"Reason: {swap_reason}. "
                if additional_info:
                    request_text += f"Details: {additional_info}. "

                if is_permanent:
                    request_text += "Please UPDATE MY PLAN permanently with a suitable alternative exercise and provide the complete updated plan in JSON format."
                else:
                    request_text += "This is just for today's workout. Please suggest 2-3 alternative exercises I can do instead."

                # Load the consultation and navigate to chat with pre-filled message
                st.session_state.consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.workout_plan = workout_plan
                st.session_state.prefilled_message = request_text
                st.session_state.show_swap_dialog = False
                st.session_state.page = "consultation"
                st.rerun()

        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_swap_dialog = False
                st.rerun()

        st.markdown("---")

    # AI Trainer Quick Chat
    with st.expander("💬 Ask Your AI Trainer", expanded=False):
        st.markdown("""
        **Your AI trainer is always available for:**
        - Quick questions about exercises
        - Modify sets/reps/intensity
        - Swap exercises (temporary or permanent)
        - Adjust training schedule
        - Nutrition and recovery advice
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💪 Increase Intensity", use_container_width=True, key="quick_intensity"):
                st.session_state.consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.workout_plan = workout_plan
                st.session_state.prefilled_message = "I'm finding the current plan too easy. Can you increase the intensity? Please provide an updated plan in JSON format."
                st.session_state.page = "consultation"
                st.rerun()

        with col2:
            if st.button("⏰ Adjust Schedule", use_container_width=True, key="quick_schedule"):
                st.session_state.consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.workout_plan = workout_plan
                st.session_state.prefilled_message = "I need to adjust my training schedule. Can we modify the plan?"
                st.session_state.page = "consultation"
                st.rerun()

        with col3:
            if st.button("❓ Ask Question", use_container_width=True, key="quick_question"):
                st.session_state.consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.workout_plan = workout_plan
                st.session_state.page = "consultation"
                st.rerun()

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

    # Sort schedule in sensible order
    if schedule:
        sorted_schedule = sort_workout_days(schedule)
        day_tabs = st.tabs(list(sorted_schedule.keys()))

        for day_tab, (day_name, day_data) in zip(day_tabs, sorted_schedule.items()):
            with day_tab:
                st.markdown(f"### {day_data.get('focus', 'Workout')}")

                exercises = day_data.get("exercises", [])

                if exercises:
                    # Display exercises with clickable links to exercise library
                    for idx, exercise in enumerate(exercises, 1):
                        exercise_name = exercise.get("name", "N/A")

                        # Exercise header with info and swap buttons
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"**{exercise.get('sequence', idx)}. {exercise_name}**")
                        with col2:
                            if st.button("🔄", key=f"{day_name}_{idx}_swap", help="Request alternative exercise"):
                                st.session_state.swap_exercise = exercise_name
                                st.session_state.swap_day = day_name
                                st.session_state.swap_consultation_id = consultation_id
                                st.session_state.show_swap_dialog = True
                                st.rerun()
                        with col3:
                            if st.button("ℹ️", key=f"{day_name}_{idx}_info", help="View exercise details"):
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

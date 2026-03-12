import streamlit as st
import pandas as pd
import time
from chat_pt.db_interface import get_user_consultations, get_workout_plan, get_conversation_history

def render_rest_timer(rest_seconds, exercise_key):
    """Render an interactive rest timer for an exercise."""
    timer_key = f"timer_{exercise_key}"
    timer_running_key = f"timer_running_{exercise_key}"
    timer_start_key = f"timer_start_{exercise_key}"
    timer_end_key = f"timer_end_{exercise_key}"

    # Initialize timer state
    if timer_running_key not in st.session_state:
        st.session_state[timer_running_key] = False
    if timer_start_key not in st.session_state:
        st.session_state[timer_start_key] = None
    if timer_end_key not in st.session_state:
        st.session_state[timer_end_key] = None

    # Check if timer is running
    if st.session_state[timer_running_key]:
        current_time = time.time()
        end_time = st.session_state[timer_end_key]
        remaining = max(0, int(end_time - current_time))

        if remaining > 0:
            # Display countdown timer
            mins = remaining // 60
            secs = remaining % 60

            # Timer display with progress bar
            progress = 1 - (remaining / rest_seconds)

            timer_html = f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 1.5rem; border-radius: 10px; text-align: center;
                        margin: 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                <div style="color: white; font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                    {mins:02d}:{secs:02d}
                </div>
                <div style="background: rgba(255,255,255,0.3); height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 1rem;">
                    <div style="background: white; height: 100%; width: {progress * 100}%; transition: width 0.3s ease;"></div>
                </div>
                <div style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">Rest Period</div>
            </div>

            <script>
            setTimeout(function() {{
                window.parent.location.reload();
            }}, 1000);
            </script>
            """
            st.markdown(timer_html, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏸️ Pause", key=f"pause_{exercise_key}", use_container_width=True):
                    st.session_state[timer_running_key] = False
                    st.session_state[timer_start_key] = None
                    st.session_state[timer_end_key] = None
                    st.rerun()
            with col2:
                if st.button("⏭️ Skip", key=f"skip_{exercise_key}", use_container_width=True):
                    st.session_state[timer_running_key] = False
                    st.session_state[timer_start_key] = None
                    st.session_state[timer_end_key] = None
                    st.success("✅ Rest complete! Ready for next set.")
                    st.rerun()
        else:
            # Timer complete
            st.session_state[timer_running_key] = False
            st.session_state[timer_start_key] = None
            st.session_state[timer_end_key] = None

            # Play completion notification
            st.markdown("""
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        padding: 1.5rem; border-radius: 10px; text-align: center;
                        margin: 1rem 0; animation: pulse 0.5s ease-in-out;">
                <div style="color: white; font-size: 2rem; margin-bottom: 0.5rem;">✅ Rest Complete!</div>
                <div style="color: rgba(255,255,255,0.9);">Ready for your next set</div>
            </div>

            <audio autoplay>
                <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLaiTkIG2u98OScTgwOUa3k7rlfGwQ9k9TuxXInBSd5yO/blEILElyx6OynVBMJRaHe8bNjGAU0jdXuxXElBSh+zPDWjDwJFl+16OupXxwFPJPT7sNwJgUohM/z1YU2Bhxqvu7mnEsLDlOy5e6zXhoEOpPU7cNxJwUmeMrw2JRCDRFYL+rsnFIKC0Oi3vG0YxgFM4vU7cNyJwUofMzv2Y48CRVftujrqV8cBTyT0+7DcCYFJ4TP89WFNgYcab7u5pxLCw5TsuXus14aBDqT1O3DcScFJnfJ8NiUQg0RWC/q7JxSCgtDot7xtGIYBTOL1O3DcicFKHzM79mOPAkVX7bo66lfHAU8k9Puw3AmBSeEz/PVhTYGHGm+7uacSwsOU7Ll7rNeGgQ6k9Ttw3EnBSZ3yfDYlEINEVgv6uycUgoLQ6Le8bRiGAUzi9Ttw3InBSh8zO/ZjjwJFV+26OupXxwFPJPT7sNwJgUnhM/z1YU2BhxqvO7mnEsLDlOy5e6zXhoEOpPU7cNxJwUmd8nw2JRCDRFYL+rsnFIKC0Oi3vG0YhgFM4vU7cNyJwUofMzv2Y48CRVftujrqV8cBTyT0+7DcCYFJ4TP89WFNgYcabzu5pxLCw5TsuXus14aBDqT1O3DcScFJnfJ8NiUQg0RWC/q7JxSCgtDot7xtGIYBTOL1O3DcicFKHzM79mOPAkVX7bo66lfHAU8k9Puw3AmBSeEz/PVhTYGHGm87uacSwsOU7Ll7rNeGgQ6k9Ttw3EnBSZ3yfDYlEINEVgv6uycUgoLQ6Le8bRiGAUzi9Ttw3InBSh8zO/ZjjwJFV+26OupXxwFPJPT7sNwJgUnhM/z1YU2BhxpvO7mnEsLDlOy5e6zXhoEOpPU7cNxJwUmd8nw2JRCDRFYL+rsnFIKC0Oi3vG0YhgFM4vU7cNyJwUofMzv2Y48CRVftujrqV8cBTyT0+7DcCYFJ4TP89WFNgYcabzu5pxLCw5TsuXus14aBDqT1O3DcScFJnfJ8NiUQg0RWC/q7JxSCgtDot7xtGIYBTOL1O3DcicFKHzM79mOPAkVX7bo66lfHAU8k9Puw3AmBSeEz/PVhTYGHGm87uacSwsOU7Ll7rNeGgQ6k9Ttw3EnBSZ3yfDYlEINEVgv6uycUgoLQ6Le8bRiGAUzi9Ttw3InBSh8zO/ZjjwJFV+26OupXxwFPJPT7sNwJgUnhM/z1YU2BhxpvO7mnEsLDlOy5e6zXhoEOpPU7cNxJwUmd8nw2JRCDRFYL+rsnFIKC0Oi3vG0YhgFM4vU7cNyJwUofMzv2Y48CRVftujrqV8cBTyT0+7DcCYFJ4TP89WFNgYcabzu5pxLCw5TsuXus14aBDqT1O3DcScFJnfJ8NiUQg0RWC/q7JxSCgtDot7xtGIYBTOL1O3DcicFKHzM79mOPAkVX7bo66lfHAU8k9Puw3AmBSeEz/PVhTYGHGm87uacSwsOU7Ll7rNeGgQ6k9Ttw3EnBSZ3yfDYlEINEVgv6uycUgoLA==" type="audio/wav">
            </audio>

            <style>
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            </style>
            """, unsafe_allow_html=True)

            time.sleep(2)
            st.rerun()

    return st.session_state[timer_running_key]

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

                # Workout session timer
                session_timer_key = f"session_timer_{day_name}"
                session_start_key = f"session_start_{day_name}"

                if session_timer_key not in st.session_state:
                    st.session_state[session_timer_key] = False
                if session_start_key not in st.session_state:
                    st.session_state[session_start_key] = None

                # Display session timer controls
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    if not st.session_state[session_timer_key]:
                        if st.button("▶️ Start Workout", key=f"start_session_{day_name}", use_container_width=True, type="primary"):
                            st.session_state[session_timer_key] = True
                            st.session_state[session_start_key] = time.time()
                            st.rerun()
                    else:
                        if st.button("⏹️ End Workout", key=f"end_session_{day_name}", use_container_width=True):
                            st.session_state[session_timer_key] = False
                            elapsed = int(time.time() - st.session_state[session_start_key])
                            st.session_state[session_start_key] = None
                            st.success(f"✅ Workout complete! Duration: {elapsed // 60}m {elapsed % 60}s")
                            st.rerun()

                with col2:
                    if st.session_state[session_timer_key]:
                        elapsed = int(time.time() - st.session_state[session_start_key])
                        mins = elapsed // 60
                        secs = elapsed % 60
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                                    padding: 0.75rem; border-radius: 8px; text-align: center; color: white;">
                            <div style="font-size: 1.5rem; font-weight: bold;">⏱️ {mins:02d}:{secs:02d}</div>
                            <div style="font-size: 0.8rem; opacity: 0.9;">Workout Duration</div>
                        </div>
                        <script>
                        setTimeout(function() {{
                            window.parent.location.reload();
                        }}, 1000);
                        </script>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                exercises = day_data.get("exercises", [])

                if exercises:
                    # Group exercises by sequence for supersets
                    # Build groups: {sequence_num: [exercises]}
                    sequence_groups = {}
                    exercise_index = 0

                    for exercise in exercises:
                        sequence = exercise.get('sequence')
                        if sequence:
                            # Extract numeric part (e.g., "2A" -> 2, "3B" -> 3)
                            import re
                            match = re.match(r'(\d+)', str(sequence))
                            if match:
                                seq_num = int(match.group(1))
                            else:
                                seq_num = None
                        else:
                            seq_num = None

                        if seq_num is not None:
                            if seq_num not in sequence_groups:
                                sequence_groups[seq_num] = []
                            sequence_groups[seq_num].append((exercise_index, exercise))
                        else:
                            # Standalone exercise
                            sequence_groups[f"solo_{exercise_index}"] = [(exercise_index, exercise)]

                        exercise_index += 1

                    # Display exercises grouped by sequence
                    display_idx = 1
                    sorted_keys = sorted([k for k in sequence_groups.keys() if isinstance(k, int)]) + \
                                  [k for k in sequence_groups.keys() if isinstance(k, str)]

                    for seq_key in sorted_keys:
                        group = sequence_groups[seq_key]

                        # Check if this is a superset (multiple exercises with same sequence)
                        is_superset = len(group) > 1 and isinstance(seq_key, int)

                        if is_superset:
                            # Display superset header
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                        padding: 0.5rem 1rem; border-radius: 8px; margin: 1rem 0 0.5rem 0;">
                                <strong style="color: white;">🔗 Superset {seq_key}</strong>
                                <span style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-left: 1rem;">
                                    Alternate between exercises with minimal rest
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                        # Display each exercise in the group
                        for orig_idx, exercise in group:
                            exercise_name = exercise.get("name", "N/A")
                            sets = exercise.get('sets', 'N/A')
                            reps = exercise.get('reps', 'N/A')
                            rest = exercise.get('rest_seconds', 60)
                            sequence = exercise.get('sequence', '')

                            exercise_key = f"{day_name}_{orig_idx}"

                            # Compact single-row layout: Name | Sets x Reps | Rest | Buttons
                            col1, col2, col3, col4 = st.columns([3, 2, 1.5, 2])

                            with col1:
                                # Show sequence indicator for supersets
                                if is_superset:
                                    st.markdown(f"**{sequence}. {exercise_name}**")
                                else:
                                    st.markdown(f"**{display_idx}. {exercise_name}**")

                                if exercise.get("notes"):
                                    st.caption(f"💡 {exercise['notes']}")

                            with col2:
                                st.markdown(f"**{sets}** × **{reps}**")

                            with col3:
                                st.caption(f"Rest: **{rest}s**")

                            with col4:
                                # Action buttons in a row
                                btn_col1, btn_col2, btn_col3 = st.columns(3)
                                with btn_col1:
                                    if st.button("⏱️", key=f"{exercise_key}_timer", help="Start rest timer", use_container_width=True):
                                        st.session_state[f"timer_running_{exercise_key}"] = True
                                        st.session_state[f"timer_start_{exercise_key}"] = time.time()
                                        st.session_state[f"timer_end_{exercise_key}"] = time.time() + rest
                                        st.rerun()
                                with btn_col2:
                                    if st.button("🔄", key=f"{exercise_key}_swap", help="Swap exercise", use_container_width=True):
                                        st.session_state.swap_exercise = exercise_name
                                        st.session_state.swap_day = day_name
                                        st.session_state.swap_consultation_id = consultation_id
                                        st.session_state.show_swap_dialog = True
                                        st.rerun()
                                with btn_col3:
                                    if st.button("ℹ️", key=f"{exercise_key}_info", help="Exercise info", use_container_width=True):
                                        st.session_state.viewing_exercise = exercise_name
                                        st.session_state.page = "exercises"
                                        st.rerun()

                            # Show timer if active for this exercise
                            timer_running = render_rest_timer(rest, exercise_key)

                        # Add separator after each exercise group
                        st.markdown("---")

                        # Increment display index only for non-superset groups
                        if not is_superset:
                            display_idx += 1
                        else:
                            display_idx += 1  # Increment once per superset group

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

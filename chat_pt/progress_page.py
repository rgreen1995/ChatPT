import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
from chat_pt.db_interface import (
    get_user_consultations,
    get_workout_plan,
    save_exercise_progress,
    get_exercise_progress,
)

def sort_workout_days(schedule_dict):
    """Sort workout days in a sensible order (days of week or numerical)."""
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_abbrev = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    keys = list(schedule_dict.keys())

    def day_sort_key(day_name):
        day_lower = day_name.lower()

        # Check for full day names
        for idx, dow in enumerate(days_of_week):
            if dow in day_lower:
                return (0, idx)

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
    """Render the progress tracking page."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊 Progress Tracking</h1>
        <p style="font-size: 1.1rem; color: #666;">Log workouts and track your fitness journey</p>
    </div>
    """, unsafe_allow_html=True)

    # Get user's completed consultations
    consultations = get_user_consultations(st.session_state.user_id)
    completed = [c for c in consultations if c["completed"]]

    if not completed:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h3 style="margin-bottom: 0.5rem;">No workout plans yet</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">Create a personalized plan first, then come back to track your progress!</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Consultation", type="primary", use_container_width=True):
                st.session_state.page = "consultation"
                st.rerun()
        return

    # Consultation selector
    st.markdown("""
    <div style="margin: 1rem 0;">
        <h3>Select Workout Plan</h3>
    </div>
    """, unsafe_allow_html=True)

    # Check if coming from plans page with selected consultation
    preselected_idx = 0
    if hasattr(st.session_state, "selected_consultation"):
        for idx, c in enumerate(completed):
            if c["id"] == st.session_state.selected_consultation:
                preselected_idx = idx
                break

    # Create descriptive names for each plan (short - 3-4 words max)
    consultation_options = []
    for c in completed:
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
        "Choose a plan",
        range(len(consultation_options)),
        format_func=lambda i: consultation_options[i],
        index=preselected_idx,
        label_visibility="collapsed"
    )

    consultation_id = completed[selected_idx]["id"]
    workout_plan = get_workout_plan(consultation_id)

    if not workout_plan:
        st.error("Error loading workout plan.")
        return

    # Two modes: Log Workout or View Progress
    tab1, tab2 = st.tabs(["📝 Log Workout", "📈 View Progress"])

    with tab1:
        render_log_workout(consultation_id, workout_plan)

    with tab2:
        render_view_progress(workout_plan)


def render_log_workout(consultation_id: int, workout_plan: dict):
    """Render the workout logging interface."""

    # Check if timer is running from plans page
    schedule = workout_plan.get("schedule", {})
    if not schedule:
        st.warning("No workout schedule found.")
        return

    # Sort schedule in sensible order
    sorted_schedule = sort_workout_days(schedule)

    # Day selector
    preselected_day = 0
    if hasattr(st.session_state, "selected_day"):
        days = list(sorted_schedule.keys())
        if st.session_state.selected_day in days:
            preselected_day = days.index(st.session_state.selected_day)

    selected_day = st.selectbox(
        "Select Training Day",
        list(sorted_schedule.keys()),
        index=preselected_day
    )

    day_data = schedule[selected_day]
    exercises = day_data.get("exercises", [])

    if not exercises:
        st.warning("No exercises found for this day.")
        return

    st.markdown(f"### {day_data.get('focus', 'Workout')}")

    # Check if any timers are running (session or rest timers)
    session_timer_key = f"session_timer_{selected_day}"
    session_start_key = f"session_start_{selected_day}"
    has_active_timer = st.session_state.get(session_timer_key, False)

    # Check for active rest timers
    if not has_active_timer:
        for key in st.session_state.keys():
            if key.startswith('timer_running_') and st.session_state.get(key, False):
                has_active_timer = True
                break

    # Add auto-refresh script if any timer is active
    if has_active_timer:
        st.markdown("""
        <script>
        setTimeout(function() {
            window.parent.location.reload();
        }, 1000);
        </script>
        """, unsafe_allow_html=True)

    # Display workout timer if running
    if st.session_state.get(session_timer_key) and st.session_state.get(session_start_key):
        elapsed = int(time.time() - st.session_state[session_start_key])
        mins = elapsed // 60
        secs = elapsed % 60

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        padding: 1rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
                <div style="font-size: 2rem; font-weight: bold;">⏱️ {mins:02d}:{secs:02d}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Workout in Progress</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Initialize exercise logging state
    if 'exercise_logs' not in st.session_state:
        st.session_state.exercise_logs = {}

    # Create grid-style workout log (similar to Strong app)
    for idx, exercise in enumerate(exercises):
        exercise_key = f"{selected_day}_{idx}_{exercise['name']}"
        rest_seconds = exercise.get('rest_seconds', 60)

        # Exercise header
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 0.75rem 1rem; border-radius: 8px; color: white; margin: 1rem 0 0.5rem 0;">
            <strong>{idx + 1}. {exercise['name']}</strong>
            <span style="opacity: 0.9; margin-left: 1rem; font-size: 0.9rem;">
                {exercise.get('sets')} × {exercise.get('reps')} | Rest: {rest_seconds}s
            </span>
        </div>
        """, unsafe_allow_html=True)

        if exercise.get('notes'):
            st.caption(f"💡 {exercise['notes']}")

        # Grid layout for sets with weight input
        # Parse sets - handle ranges like "3-4" by taking the lower bound
        sets_value = exercise.get('sets', 3)
        if isinstance(sets_value, str):
            if '-' in sets_value:
                try:
                    num_sets = int(sets_value.split('-')[0])
                except:
                    num_sets = 3
            else:
                try:
                    num_sets = int(sets_value)
                except:
                    num_sets = 3
        else:
            num_sets = int(sets_value) if isinstance(sets_value, (int, float)) else 3

        # Header row
        col_headers = st.columns([1, 2, 2, 2, 1.5])
        col_headers[0].markdown("**Set**")
        col_headers[1].markdown("**Reps**")
        col_headers[2].markdown("**Weight**")
        col_headers[3].markdown("**Notes**")
        col_headers[4].markdown("**Timer**")

        # Initialize logs for this exercise
        if exercise_key not in st.session_state.exercise_logs:
            # Parse reps - handle ranges like "8-10" by taking the midpoint
            reps_value = exercise.get('reps', 10)
            if isinstance(reps_value, str):
                # Handle range like "8-10"
                if '-' in reps_value:
                    try:
                        parts = reps_value.split('-')
                        default_reps = int((int(parts[0]) + int(parts[1])) / 2)
                    except:
                        default_reps = 10
                else:
                    try:
                        default_reps = int(reps_value)
                    except:
                        default_reps = 10
            else:
                default_reps = int(reps_value) if isinstance(reps_value, (int, float)) else 10

            st.session_state.exercise_logs[exercise_key] = {
                'sets': [{'reps': default_reps, 'weight': 0.0, 'notes': '', 'completed': False}
                         for _ in range(num_sets)]
            }

        # Display each set
        for set_idx in range(num_sets):
            cols = st.columns([1, 2, 2, 2, 1.5])

            with cols[0]:
                st.markdown(f"**{set_idx + 1}**")

            with cols[1]:
                reps = st.number_input(
                    "Reps",
                    min_value=1,
                    max_value=100,
                    value=st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['reps'],
                    key=f"reps_{exercise_key}_{set_idx}",
                    label_visibility="collapsed"
                )
                st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['reps'] = reps

            with cols[2]:
                weight = st.number_input(
                    "Weight",
                    min_value=0.0,
                    max_value=1000.0,
                    step=2.5,
                    value=st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['weight'],
                    key=f"weight_{exercise_key}_{set_idx}",
                    label_visibility="collapsed"
                )
                st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['weight'] = weight

            with cols[3]:
                notes = st.text_input(
                    "Notes",
                    value=st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['notes'],
                    key=f"notes_{exercise_key}_{set_idx}",
                    placeholder="Feel, RPE, etc.",
                    label_visibility="collapsed"
                )
                st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['notes'] = notes

            with cols[4]:
                timer_key = f"timer_{exercise_key}_{set_idx}"
                timer_running_key = f"timer_running_{timer_key}"
                timer_end_key = f"timer_end_{timer_key}"

                if timer_running_key not in st.session_state:
                    st.session_state[timer_running_key] = False

                if not st.session_state[timer_running_key]:
                    if st.button("⏱️", key=f"start_{timer_key}", help=f"Start {rest_seconds}s rest", use_container_width=True):
                        st.session_state[timer_running_key] = True
                        st.session_state[timer_end_key] = time.time() + rest_seconds
                        st.session_state.exercise_logs[exercise_key]['sets'][set_idx]['completed'] = True
                        st.rerun()
                else:
                    remaining = max(0, int(st.session_state[timer_end_key] - time.time()))
                    if remaining > 0:
                        st.markdown(f"""
                        <div style="text-align: center; font-weight: bold; color: #667eea;">
                            {remaining}s
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.session_state[timer_running_key] = False
                        st.markdown("✅")

        st.markdown("<br>", unsafe_allow_html=True)

    # Save workout button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save Workout", type="primary", use_container_width=True, key="save_workout"):
            # Save all exercises
            for exercise in exercises:
                exercise_key = f"{selected_day}_{exercises.index(exercise)}_{exercise['name']}"
                if exercise_key in st.session_state.exercise_logs:
                    logs = st.session_state.exercise_logs[exercise_key]['sets']
                    for set_log in logs:
                        save_exercise_progress(
                            user_id=st.session_state.user_id,
                            consultation_id=consultation_id,
                            exercise_name=exercise["name"],
                            day=selected_day,
                            sets=1,  # Each set logged individually
                            reps=set_log['reps'],
                            weight=set_log['weight'],
                            notes=set_log['notes']
                        )

            # Stop timer
            if st.session_state.get(session_timer_key):
                st.session_state[session_timer_key] = False
                elapsed = int(time.time() - st.session_state[session_start_key])
                st.session_state[session_start_key] = None

            # Clear logs
            st.session_state.exercise_logs = {}

            st.success("✅ Workout logged successfully!")
            st.balloons()
            time.sleep(1)
            st.rerun()


def render_view_progress(workout_plan: dict):
    """Render the progress viewing interface."""
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h3>Your Progress Over Time</h3>
    </div>
    """, unsafe_allow_html=True)

    schedule = workout_plan.get("schedule", {})

    # Get all unique exercises from the plan
    all_exercises = []
    for day_data in schedule.values():
        for exercise in day_data.get("exercises", []):
            exercise_name = exercise.get("name")
            if exercise_name and exercise_name not in all_exercises:
                all_exercises.append(exercise_name)

    if not all_exercises:
        st.warning("No exercises found in this plan.")
        return

    # Exercise selector
    selected_exercise = st.selectbox("Select Exercise", all_exercises)

    # Get progress for selected exercise
    progress = get_exercise_progress(st.session_state.user_id, selected_exercise)

    if not progress:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📈</div>
            <h4 style="margin-bottom: 0.5rem;">No progress logged yet for {selected_exercise}</h4>
            <p style="color: #666;">Switch to the "Log Workout" tab to record your first session!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Display progress table
    st.markdown(f"### Progress for: {selected_exercise}")

    df = pd.DataFrame(progress)
    df["completed_at"] = pd.to_datetime(df["completed_at"])
    df = df.sort_values("completed_at", ascending=False)

    # Display table
    display_df = df[["completed_at", "day", "sets", "reps", "weight", "notes"]].copy()
    display_df["completed_at"] = display_df["completed_at"].dt.strftime("%Y-%m-%d %H:%M")
    display_df.columns = ["Date", "Day", "Sets", "Reps", "Weight", "Notes"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Progress charts
    st.markdown("### 📈 Progress Charts")

    col1, col2 = st.columns(2)

    with col1:
        # Weight progression chart
        if df["weight"].sum() > 0:
            fig_weight = px.line(
                df.sort_values("completed_at"),
                x="completed_at",
                y="weight",
                title="Weight Progression",
                labels={"completed_at": "Date", "weight": "Weight (lbs/kg)"},
                markers=True
            )
            fig_weight.update_layout(showlegend=False)
            st.plotly_chart(fig_weight, use_container_width=True)
        else:
            st.info("No weight data logged yet")

    with col2:
        # Volume chart (sets × reps × weight)
        df_sorted = df.sort_values("completed_at")
        df_sorted["volume"] = df_sorted["sets"] * df_sorted["reps"] * df_sorted["weight"]

        if df_sorted["volume"].sum() > 0:
            fig_volume = px.line(
                df_sorted,
                x="completed_at",
                y="volume",
                title="Training Volume (Sets × Reps × Weight)",
                labels={"completed_at": "Date", "volume": "Volume"},
                markers=True
            )
            fig_volume.update_layout(showlegend=False)
            st.plotly_chart(fig_volume, use_container_width=True)
        else:
            st.info("No volume data to display")

    # Stats summary
    st.markdown("### 📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sessions", len(progress))

    with col2:
        max_weight = df["weight"].max()
        st.metric("Max Weight", f"{max_weight} lbs/kg")

    with col3:
        avg_sets = df["sets"].mean()
        st.metric("Avg Sets", f"{avg_sets:.1f}")

    with col4:
        avg_reps = df["reps"].mean()
        st.metric("Avg Reps", f"{avg_reps:.1f}")

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from chat_pt.database import (
    get_user_consultations,
    get_workout_plan,
    save_exercise_progress,
    get_exercise_progress,
)

def render():
    """Render the progress tracking page."""
    st.title("📊 Progress Tracking")

    # Get user's completed consultations
    consultations = get_user_consultations(st.session_state.user_id)
    completed = [c for c in consultations if c["completed"]]

    if not completed:
        st.warning("No workout plans found. Create a plan first!")
        if st.button("Start Consultation"):
            st.session_state.page = "consultation"
            st.rerun()
        return

    # Consultation selector
    st.subheader("Select Workout Plan")

    # Check if coming from plans page with selected consultation
    preselected_idx = 0
    if hasattr(st.session_state, "selected_consultation"):
        for idx, c in enumerate(completed):
            if c["id"] == st.session_state.selected_consultation:
                preselected_idx = idx
                break

    consultation_options = [
        f"Plan {c['id']} - {c['created_at']}" for c in completed
    ]

    selected_idx = st.selectbox(
        "Choose a plan",
        range(len(consultation_options)),
        format_func=lambda i: consultation_options[i],
        index=preselected_idx
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
    st.subheader("Log Your Workout")

    schedule = workout_plan.get("schedule", {})

    if not schedule:
        st.warning("No workout schedule found.")
        return

    # Day selector
    preselected_day = 0
    if hasattr(st.session_state, "selected_day"):
        days = list(schedule.keys())
        if st.session_state.selected_day in days:
            preselected_day = days.index(st.session_state.selected_day)

    selected_day = st.selectbox(
        "Select Training Day",
        list(schedule.keys()),
        index=preselected_day
    )

    day_data = schedule[selected_day]
    exercises = day_data.get("exercises", [])

    if not exercises:
        st.warning("No exercises found for this day.")
        return

    st.markdown(f"### {day_data.get('focus', 'Workout')}")
    st.markdown("---")

    # Create form for logging
    with st.form("workout_log_form"):
        logged_exercises = []

        for idx, exercise in enumerate(exercises):
            st.markdown(f"#### {idx + 1}. {exercise['name']}")

            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

            with col1:
                st.caption(f"Prescribed: {exercise.get('sets')} sets × {exercise.get('reps')} reps")
                if exercise.get('notes'):
                    st.caption(f"💡 {exercise['notes']}")

            with col2:
                sets = st.number_input(
                    "Sets",
                    min_value=1,
                    max_value=20,
                    value=int(exercise.get('sets', 3)) if isinstance(exercise.get('sets'), (int, float)) else 3,
                    key=f"sets_{idx}"
                )

            with col3:
                reps = st.number_input(
                    "Reps",
                    min_value=1,
                    max_value=100,
                    value=10,
                    key=f"reps_{idx}"
                )

            with col4:
                weight = st.number_input(
                    "Weight (lbs/kg)",
                    min_value=0.0,
                    max_value=1000.0,
                    step=5.0,
                    value=0.0,
                    key=f"weight_{idx}"
                )

            notes = st.text_input(
                "Notes (optional)",
                key=f"notes_{idx}",
                placeholder="How did it feel? Any issues?"
            )

            logged_exercises.append({
                "name": exercise["name"],
                "sets": sets,
                "reps": reps,
                "weight": weight,
                "notes": notes
            })

            st.markdown("---")

        submitted = st.form_submit_button("💾 Save Workout", type="primary", use_container_width=True)

        if submitted:
            # Save all exercises
            for exercise_data in logged_exercises:
                save_exercise_progress(
                    user_id=st.session_state.user_id,
                    consultation_id=consultation_id,
                    exercise_name=exercise_data["name"],
                    day=selected_day,
                    sets=exercise_data["sets"],
                    reps=exercise_data["reps"],
                    weight=exercise_data["weight"],
                    notes=exercise_data["notes"]
                )

            st.success("✅ Workout logged successfully!")
            st.balloons()


def render_view_progress(workout_plan: dict):
    """Render the progress viewing interface."""
    st.subheader("Your Progress Over Time")

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
        st.info(f"No progress logged yet for {selected_exercise}. Log your first workout!")
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

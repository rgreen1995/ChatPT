import streamlit as st
import re

def render_exercise_detail(exercise_name: str, exercises_data: list):
    """Render detailed exercise information with video embed."""
    # Find the exercise in the data
    exercise = next((ex for ex in exercises_data if ex["name"].lower() == exercise_name.lower()), None)

    if not exercise:
        st.error(f"Exercise '{exercise_name}' not found in library")
        return

    # Header
    st.title(f"🏋️ {exercise['name']}")

    # Badges
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Category", exercise['category'])
    with col2:
        st.metric("Difficulty", exercise['difficulty'])
    with col3:
        st.metric("Equipment", exercise['equipment'])
    with col4:
        st.metric("Primary Muscles", exercise['primary_muscles'].split(',')[0])

    st.markdown("---")

    # YouTube Video Embed
    if exercise.get('youtube_url'):
        st.subheader("📹 Video Demonstration")

        # Extract YouTube video ID
        video_id = extract_youtube_id(exercise['youtube_url'])
        if video_id:
            # Embed video using iframe
            st.markdown(f"""
                <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
                    <iframe
                        src="https://www.youtube.com/embed/{video_id}"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                    ></iframe>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.video(exercise['youtube_url'])

    st.markdown("---")

    # Instructions
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📝 Instructions")
        st.markdown(exercise['instructions'])

    with col_right:
        st.subheader("✅ Form Cues")
        st.markdown(exercise['form_cues'])

    # Additional Information
    st.markdown("---")
    st.subheader("💪 Muscles Worked")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Primary:** {exercise['primary_muscles']}")
    with col2:
        if exercise.get('secondary_muscles'):
            st.write(f"**Secondary:** {exercise['secondary_muscles']}")

    # Back button
    st.markdown("---")
    if st.button("← Back to Plans", use_container_width=True):
        if 'viewing_exercise' in st.session_state:
            del st.session_state.viewing_exercise
        st.rerun()


def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    # Handle different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([^&]+)',
        r'(?:youtu\.be\/)([^?]+)',
        r'(?:youtube\.com\/embed\/)([^?]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def render():
    """Render the exercise library browser."""
    from chat_pt.exercise_data import EXERCISE_LIBRARY

    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📚 Exercise Library</h1>
        <p style="font-size: 1.1rem; color: #666;">Browse 40+ exercises with video demonstrations</p>
    </div>
    """, unsafe_allow_html=True)

    # Body part groupings
    BODY_PART_GROUPS = {
        "Upper Body": ["Chest", "Back", "Shoulders", "Arms"],
        "Lower Body": ["Legs"],
        "Core": ["Core"],
    }

    # Check if a body part group has been selected
    if 'selected_body_part' not in st.session_state:
        st.session_state.selected_body_part = None

    # If no body part selected, show body part selection
    if st.session_state.selected_body_part is None:
        st.markdown("""
        <div style="margin: 1rem 0;">
            <h3>Select a body part to browse exercises</h3>
        </div>
        """, unsafe_allow_html=True)

        # Create body part cards with gradients
        cols = st.columns(3)

        body_parts = [
            {"name": "Upper Body", "emoji": "💪", "description": "Chest, Back, Shoulders, Arms", "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
            {"name": "Lower Body", "emoji": "🦵", "description": "Legs, Glutes, Calves", "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"},
            {"name": "Core", "emoji": "🔥", "description": "Abs, Obliques, Lower Back", "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"},
        ]

        for idx, body_part in enumerate(body_parts):
            with cols[idx]:
                # Count exercises in this body part
                exercise_count = len([ex for ex in EXERCISE_LIBRARY if ex["category"] in BODY_PART_GROUPS.get(body_part['name'], [])])

                st.markdown(f"""
                <div style="background: {body_part['gradient']}; padding: 2rem 1.5rem; border-radius: 10px; text-align: center; color: white; min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">{body_part['emoji']}</div>
                    <h3 style="margin: 0.5rem 0; color: white;">{body_part['name']}</h3>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">{body_part['description']}</p>
                    <div style="font-size: 1.2rem; margin-top: 1rem; font-weight: bold;">{exercise_count} exercises</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(f"Browse {body_part['name']}", key=f"select_{body_part['name']}", use_container_width=True, type="primary"):
                    st.session_state.selected_body_part = body_part['name']
                    st.rerun()

        return

    # Body part is selected - show exercises for that body part
    if st.button(f"← Back to Body Parts"):
        st.session_state.selected_body_part = None
        st.rerun()

    st.subheader(f"💪 {st.session_state.selected_body_part} Exercises")

    # Filter exercises by selected body part
    selected_categories = BODY_PART_GROUPS.get(st.session_state.selected_body_part, [])
    filtered_exercises = [ex for ex in EXERCISE_LIBRARY if ex["category"] in selected_categories]

    # Search within selected body part
    search = st.text_input("🔍 Search exercises", placeholder="e.g., bench press, squat...")

    if search:
        filtered_exercises = [
            ex for ex in filtered_exercises
            if search.lower() in ex["name"].lower() or
               search.lower() in ex["primary_muscles"].lower() or
               search.lower() in ex.get("secondary_muscles", "").lower()
        ]

    # Group by specific muscle category
    exercises_by_category = {}
    for ex in filtered_exercises:
        cat = ex["category"]
        if cat not in exercises_by_category:
            exercises_by_category[cat] = []
        exercises_by_category[cat].append(ex)

    # Display results
    st.write(f"**{len(filtered_exercises)} exercises found**")
    st.markdown("---")

    if not filtered_exercises:
        st.info("No exercises found matching your search criteria.")
        return

    # Display exercises grouped by muscle category
    for category, exercises in sorted(exercises_by_category.items()):
        st.subheader(f"🎯 {category}")

        cols = st.columns(2)
        for idx, exercise in enumerate(exercises):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"**{exercise['name']}**")
                    st.caption(f"{exercise['difficulty']} • {exercise['equipment']}")
                    st.caption(f"**Targets:** {exercise['primary_muscles']}")

                    if st.button(f"View Details →", key=f"view_{exercise['name']}", use_container_width=True):
                        st.session_state.viewing_exercise = exercise["name"]
                        st.rerun()

                    st.markdown("---")

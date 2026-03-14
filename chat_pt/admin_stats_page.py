import streamlit as st
from chat_pt.db_interface import get_missing_exercise_requests

def render():
    """Render admin stats page for missing exercise requests."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊 Missing Exercise Requests</h1>
        <p style="font-size: 1.1rem; color: #666;">Track which exercises users are requesting</p>
    </div>
    """, unsafe_allow_html=True)

    # Get missing exercise requests
    requests = get_missing_exercise_requests(min_requests=1, limit=100)

    if not requests:
        st.info("No missing exercise requests yet!")
        return

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 2rem;">
        <div style="font-size: 2rem; font-weight: bold;">{len(requests)}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">Unique Exercises Requested</div>
    </div>
    """, unsafe_allow_html=True)

    # Filter options
    st.subheader("Filter Options")
    col1, col2 = st.columns(2)

    with col1:
        min_requests_filter = st.slider(
            "Minimum request count",
            min_value=1,
            max_value=max([r['request_count'] for r in requests], default=1),
            value=1
        )

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Requested", "Most Recent"]
        )

    # Filter requests
    filtered_requests = [r for r in requests if r['request_count'] >= min_requests_filter]

    # Sort
    if sort_by == "Most Recent":
        filtered_requests.sort(key=lambda x: x['last_requested'], reverse=True)

    st.markdown("---")
    st.subheader(f"Top {len(filtered_requests)} Missing Exercises")

    # Display as table
    for idx, req in enumerate(filtered_requests, 1):
        col1, col2, col3 = st.columns([3, 1, 2])

        with col1:
            st.markdown(f"**{idx}. {req['exercise_name']}**")

        with col2:
            # Badge for request count
            count = req['request_count']
            badge_color = "#28a745" if count >= 5 else "#ffc107" if count >= 3 else "#6c757d"
            st.markdown(f"""
            <div style="background: {badge_color}; color: white; padding: 0.25rem 0.75rem;
                        border-radius: 12px; text-align: center; font-weight: bold;">
                {count} request{"s" if count > 1 else ""}
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.caption(f"Last: {req['last_requested']}")

        st.markdown("---")

    # Export options
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Export Data")

    # Create CSV content
    csv_content = "Exercise Name,Request Count,Last Requested\n"
    for req in filtered_requests:
        csv_content += f"{req['exercise_name']},{req['request_count']},{req['last_requested']}\n"

    st.download_button(
        label="📥 Download as CSV",
        data=csv_content,
        file_name="missing_exercises.csv",
        mime="text/csv",
        use_container_width=True
    )

    # Instructions
    st.markdown("---")
    with st.expander("💡 How to Use This Data"):
        st.markdown("""
        **Updating the Exercise Library:**

        1. **Prioritize High-Request Exercises**: Focus on exercises with 5+ requests first
        2. **Research & Create Content**: For each exercise:
           - Find a quality YouTube tutorial
           - Write instructions and form cues
           - Categorize by muscle group and difficulty
        3. **Add to Library**: Update `chat_pt/exercise_data.py` with new exercises
        4. **Update LLM Prompts**: Consider adding these to the AI trainer's knowledge

        **Quick Win**: Exercises with 3+ requests are good candidates for immediate addition.
        """)

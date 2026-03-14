import streamlit as st
from chat_pt.db_interface import get_user_consultations, get_nutrition_plan, get_conversation_history

def render():
    """Render the nutrition plans page."""

    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🥗 My Nutrition Plans</h1>
        <p style="font-size: 1.1rem; color: #666;">Your personalized nutrition programs</p>
    </div>
    """, unsafe_allow_html=True)

    # Get user's consultations
    consultations = get_user_consultations(st.session_state.user_id)

    if not consultations:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🥗</div>
            <h3 style="margin-bottom: 0.5rem;">No nutrition plans yet</h3>
            <p style="color: #666; margin-bottom: 1.5rem;">Start a nutrition consultation to create your first personalized plan!</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Start Nutrition Consultation", type="primary", use_container_width=True):
                st.session_state.page = "nutrition_consultation"
                st.rerun()
        return

    # Filter nutrition consultations with plans
    from chat_pt.db_interface import get_consultation_type
    nutrition_consultations = []
    for c in consultations:
        if get_consultation_type(c['id']) == 'nutrition':
            plan = get_nutrition_plan(c['id'])
            if plan:
                nutrition_consultations.append(c)

    if not nutrition_consultations:
        st.markdown("""
        <div style="background: #fff3cd; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #ffc107; margin: 2rem 0;">
            <h4 style="margin: 0 0 0.5rem 0;">⏳ Nutrition Consultation in Progress</h4>
            <p style="margin: 0; color: #666;">You have consultations in progress but no completed nutrition plans yet.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Continue Nutrition Consultation", type="primary", use_container_width=True):
            st.session_state.page = "nutrition_consultation"
            st.rerun()
        return

    # Consultation selector
    st.markdown("""
    <div style="margin: 1rem 0;">
        <h3>Select a Plan</h3>
    </div>
    """, unsafe_allow_html=True)

    # Create descriptive names for each plan
    consultation_options = []
    for c in nutrition_consultations:
        plan = get_nutrition_plan(c['id'])
        if plan:
            # Extract key details
            calories = plan.get('daily_calories')
            goal = plan.get('goal', '').replace('_', ' ').title()

            # Build concise name
            if calories and goal:
                plan_name = f"{calories} cal • {goal}"
            elif calories:
                plan_name = f"{calories} cal/day"
            else:
                # Use date as fallback
                import datetime
                try:
                    date_obj = datetime.datetime.fromisoformat(c['created_at'])
                    plan_name = date_obj.strftime("%b %d, %Y")
                except:
                    plan_name = "Nutrition Plan"

            consultation_options.append(plan_name)
        else:
            consultation_options.append("Nutrition Plan")

    selected_idx = st.selectbox(
        "Choose a nutrition plan to view",
        range(len(consultation_options)),
        format_func=lambda i: consultation_options[i],
        label_visibility="collapsed"
    )

    selected_consultation = nutrition_consultations[selected_idx]
    consultation_id = selected_consultation["id"]

    # Load nutrition plan
    nutrition_plan = get_nutrition_plan(consultation_id)

    if not nutrition_plan:
        st.error("Error loading nutrition plan.")
        return

    # AI Nutrition Coach Quick Chat
    with st.expander("💬 Ask Your AI Nutrition Coach", expanded=False):
        st.markdown("""
        **Your AI nutrition coach is always available for:**
        - Quick questions about meals or foods
        - Adjust calories or macros
        - Make it vegetarian/vegan
        - Change meal frequency
        - Swap specific foods
        - Budget-friendly alternatives
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📉 Lower Calories", use_container_width=True, key="quick_lower_cal"):
                st.session_state.nutrition_consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.nutrition_plan = nutrition_plan
                st.session_state.prefilled_message = "I need to lower my daily calories. Can you adjust the plan to reduce calories while maintaining good nutrition? Please provide an updated plan in JSON format."
                st.session_state.page = "nutrition_consultation"
                st.rerun()

        with col2:
            if st.button("🌱 Make Vegetarian", use_container_width=True, key="quick_vegetarian"):
                st.session_state.nutrition_consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.nutrition_plan = nutrition_plan
                st.session_state.prefilled_message = "Can you make this nutrition plan vegetarian? Please swap out any meat/fish for vegetarian protein sources and provide the updated plan in JSON."
                st.session_state.page = "nutrition_consultation"
                st.rerun()

        with col3:
            if st.button("❓ Ask Question", use_container_width=True, key="quick_question"):
                st.session_state.nutrition_consultation_id = consultation_id
                st.session_state.messages = get_conversation_history(consultation_id)
                st.session_state.nutrition_plan = nutrition_plan
                st.session_state.page = "nutrition_consultation"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Display plan summary with gradient cards
    col1, col2, col3 = st.columns(3)

    with col1:
        calories = nutrition_plan.get("daily_calories", "N/A")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{calories}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Daily Calories</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if 'macros' in nutrition_plan:
            protein = nutrition_plan['macros'].get('protein_g', 'N/A')
        else:
            protein = 'N/A'
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{protein}g</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Protein Daily</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        goal = nutrition_plan.get('goal', 'N/A').replace('_', ' ').title()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">{goal}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Goal</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Display summary
    if "summary" in nutrition_plan:
        st.markdown("""
        <div style="margin: 1rem 0;">
            <h3>📝 Plan Overview</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
            {nutrition_plan["summary"]}
        </div>
        """, unsafe_allow_html=True)

    # Display macros breakdown
    if "macros" in nutrition_plan:
        st.subheader("🎯 Daily Macros")
        macros = nutrition_plan["macros"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #1976d2;">{macros.get('protein_g', '?')}g</div>
                <div style="color: #666; font-size: 0.9rem;">Protein</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #f57c00;">{macros.get('carbs_g', '?')}g</div>
                <div style="color: #666; font-size: 0.9rem;">Carbs</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background: #f3e5f5; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #7b1fa2;">{macros.get('fats_g', '?')}g</div>
                <div style="color: #666; font-size: 0.9rem;">Fats</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Display meal structure
    if "meal_structure" in nutrition_plan:
        st.subheader("🍽️ Meal Structure")
        meal_structure = nutrition_plan["meal_structure"]

        col1, col2 = st.columns(2)
        with col1:
            meals_per_day = meal_structure.get('meals_per_day', 'N/A')
            st.info(f"**Meals per day:** {meals_per_day}")

        with col2:
            timing_notes = meal_structure.get('timing_notes', 'N/A')
            st.info(f"**Timing:** {timing_notes}")

        st.markdown("<br>", unsafe_allow_html=True)

    # Display meal plans (training day and rest day)
    if "days" in nutrition_plan:
        st.subheader("📅 Daily Meal Plans")

        days = nutrition_plan["days"]
        day_tabs = st.tabs(list(days.keys()))

        for day_tab, (day_name, day_data) in zip(day_tabs, days.items()):
            with day_tab:
                st.markdown(f"### {day_name.replace('_', ' ').title()}")

                meals = day_data.get("meals", [])
                if meals:
                    for i, meal in enumerate(meals, 1):
                        meal_name = meal.get("name", f"Meal {i}")
                        foods = meal.get("foods", [])
                        notes = meal.get("notes", "")

                        # Display meal card
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #4facfe;">
                            <h4 style="margin: 0 0 0.5rem 0;">{meal_name}</h4>
                        </div>
                        """, unsafe_allow_html=True)

                        # Display foods as bullet list
                        if foods:
                            st.markdown("**Foods:**")
                            for food in foods:
                                st.markdown(f"- {food}")

                        # Display notes if present
                        if notes:
                            st.caption(f"💡 {notes}")

                        st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.info("No meals specified for this day type.")

    # Display shopping notes
    if "shopping_notes" in nutrition_plan and nutrition_plan["shopping_notes"]:
        st.subheader("🛒 Shopping Notes")
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
            {nutrition_plan["shopping_notes"]}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display adherence notes
    if "adherence_notes" in nutrition_plan and nutrition_plan["adherence_notes"]:
        st.subheader("💪 Adherence Tips")
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
            {nutrition_plan["adherence_notes"]}
        </div>
        """, unsafe_allow_html=True)

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
        if st.button("💬 Continue Consultation", use_container_width=True):
            # Resume the consultation with this plan's history
            st.session_state.nutrition_consultation_id = consultation_id
            st.session_state.messages = get_conversation_history(consultation_id)
            st.session_state.nutrition_plan = nutrition_plan
            st.session_state.page = "nutrition_consultation"
            st.rerun()

    with col2:
        if st.button("🏋️ View Workout Plans", use_container_width=True):
            st.session_state.page = "plans"
            st.rerun()

    with col3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

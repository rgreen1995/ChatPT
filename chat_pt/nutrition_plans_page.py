import streamlit as st
from chat_pt.db_interface import get_user_consultations, get_nutrition_plan, get_conversation_history

def safe_get_numeric(data, key, default='N/A'):
    """Safely extract and convert numeric values from data."""
    try:
        value = data.get(key)
        if value is None:
            return default
        return int(float(value))
    except (ValueError, TypeError, AttributeError):
        return default

def safe_get_string(data, key, default='Not Specified'):
    """Safely extract string values from data."""
    try:
        value = data.get(key, default)
        if value is None or (isinstance(value, str) and not value.strip()):
            return default
        return str(value)
    except (TypeError, AttributeError):
        return default

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
        if plan and isinstance(plan, dict):
            # Extract key details - check for split calories
            calories = safe_get_numeric(plan, 'daily_calories', None)
            training_cal = safe_get_numeric(plan, 'daily_calories_training', None)
            rest_cal = safe_get_numeric(plan, 'daily_calories_rest', None)
            goal = safe_get_string(plan, 'goal', '')
            if goal and isinstance(goal, str):
                goal = goal.replace('_', ' ').title()

            # Build concise name
            if training_cal and training_cal != 'N/A' and rest_cal and rest_cal != 'N/A' and goal:
                plan_name = f"{training_cal}/{rest_cal} cal • {goal}"
            elif training_cal and training_cal != 'N/A' and rest_cal and rest_cal != 'N/A':
                plan_name = f"{training_cal}/{rest_cal} cal/day"
            elif calories and calories != 'N/A' and goal:
                plan_name = f"{calories} cal • {goal}"
            elif calories and calories != 'N/A':
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

    if not nutrition_plan or not isinstance(nutrition_plan, dict):
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
        # Handle split calories with defensive access
        training_cal = safe_get_numeric(nutrition_plan, 'daily_calories_training', None)
        rest_cal = safe_get_numeric(nutrition_plan, 'daily_calories_rest', None)
        calories = safe_get_numeric(nutrition_plan, 'daily_calories', None)

        if training_cal and training_cal != 'N/A' and rest_cal and rest_cal != 'N/A':
            calories_display = f"""
            <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 0.3rem;">Training: {training_cal}</div>
            <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">Rest: {rest_cal}</div>
            """
            label = "Daily Calories"
        elif calories and calories != 'N/A':
            calories_display = f'<div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{calories}</div>'
            label = "Daily Calories"
        else:
            calories_display = '<div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">N/A</div>'
            label = "Daily Calories"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            {calories_display}
            <div style="font-size: 0.9rem; opacity: 0.9;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Handle split or single macros for protein with defensive access
        protein = 'N/A'
        try:
            if 'macros' in nutrition_plan and nutrition_plan['macros']:
                macros = nutrition_plan['macros']
                if isinstance(macros, dict):
                    # Check for split macros
                    if 'training_day' in macros and isinstance(macros.get('training_day'), dict):
                        training_protein = safe_get_numeric(macros['training_day'], 'protein_g', None)
                        rest_protein = None
                        if 'rest_day' in macros and isinstance(macros.get('rest_day'), dict):
                            rest_protein = safe_get_numeric(macros['rest_day'], 'protein_g', None)

                        if training_protein and training_protein != 'N/A' and rest_protein and rest_protein != 'N/A':
                            protein = f"{training_protein}/{rest_protein}"
                        elif training_protein and training_protein != 'N/A':
                            protein = str(training_protein)
                    else:
                        # Single macro structure
                        protein_val = safe_get_numeric(macros, 'protein_g', None)
                        if protein_val and protein_val != 'N/A':
                            protein = str(protein_val)
        except (TypeError, AttributeError):
            protein = 'N/A'

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{protein}g</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Protein Daily</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        goal = safe_get_string(nutrition_plan, 'goal', 'Not Specified')
        if goal and isinstance(goal, str) and goal != 'Not Specified':
            goal = goal.replace('_', ' ').title()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">{goal}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Goal</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Display summary with defensive check
    if "summary" in nutrition_plan and nutrition_plan["summary"]:
        summary_text = safe_get_string(nutrition_plan, "summary", "")
        if summary_text and summary_text != 'Not Specified':
            st.markdown("""
            <div style="margin: 1rem 0;">
                <h3>📝 Plan Overview</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea;">
                {summary_text}
            </div>
            """, unsafe_allow_html=True)

    # Display macros breakdown
    if "macros" in nutrition_plan:
        st.subheader("🎯 Daily Macros")
        macros = nutrition_plan["macros"]

        # Check if macros are split between training and rest days
        if isinstance(macros, dict) and 'training_day' in macros:
            # Display split macros
            st.markdown("**Training Day:**")
            training_macros = macros.get('training_day', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #1976d2;">{training_macros.get('protein_g', '?')}g</div>
                    <div style="color: #666; font-size: 0.9rem;">Protein</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #f57c00;">{training_macros.get('carbs_g', '?')}g</div>
                    <div style="color: #666; font-size: 0.9rem;">Carbs</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style="background: #f3e5f5; padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #7b1fa2;">{training_macros.get('fats_g', '?')}g</div>
                    <div style="color: #666; font-size: 0.9rem;">Fats</div>
                </div>
                """, unsafe_allow_html=True)

            if 'rest_day' in macros:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Rest Day:**")
                rest_macros = macros.get('rest_day', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #1976d2;">{rest_macros.get('protein_g', '?')}g</div>
                        <div style="color: #666; font-size: 0.9rem;">Protein</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #f57c00;">{rest_macros.get('carbs_g', '?')}g</div>
                        <div style="color: #666; font-size: 0.9rem;">Carbs</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div style="background: #f3e5f5; padding: 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #7b1fa2;">{rest_macros.get('fats_g', '?')}g</div>
                        <div style="color: #666; font-size: 0.9rem;">Fats</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Display single set of macros
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
        try:
            st.subheader("🍽️ Meal Structure")
            meal_structure = nutrition_plan["meal_structure"]

            # Validate meal_structure is a dict
            if isinstance(meal_structure, dict):
                col1, col2 = st.columns(2)
                with col1:
                    meals_per_day = safe_get_numeric(meal_structure, 'meals_per_day', 'N/A')
                    st.info(f"**Meals per day:** {meals_per_day}")

                with col2:
                    timing_notes = safe_get_string(meal_structure, 'timing_notes', 'N/A')
                    st.info(f"**Timing:** {timing_notes}")

                st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.warning("Could not display meal structure information.")

    # Display meal rotation notes if available (for weekly plans)
    meal_rotation_notes = safe_get_string(nutrition_plan, "meal_rotation_notes", "")
    if meal_rotation_notes and meal_rotation_notes != "Not Specified":
        st.markdown("""
        <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
            <h4 style="margin: 0 0 0.5rem 0;">🔄 Meal Rotation Notes</h4>
        """, unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0;'>{meal_rotation_notes}</p></div>", unsafe_allow_html=True)

    # Display meal plans - handle both weekly_plan and days formats
    has_weekly_plan = "weekly_plan" in nutrition_plan and isinstance(nutrition_plan["weekly_plan"], dict)
    has_days_plan = "days" in nutrition_plan and isinstance(nutrition_plan["days"], dict)

    if has_weekly_plan:
        # New weekly plan format (Monday-Sunday)
        try:
            st.subheader("📅 Weekly Meal Plan")

            weekly_plan = nutrition_plan["weekly_plan"]

            # Define days in order
            day_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            day_display_names = {
                "monday": "Monday",
                "tuesday": "Tuesday",
                "wednesday": "Wednesday",
                "thursday": "Thursday",
                "friday": "Friday",
                "saturday": "Saturday",
                "sunday": "Sunday"
            }

            # Filter to only days that exist in the plan
            available_days = [day for day in day_order if day in weekly_plan]

            if not available_days:
                st.info("No weekly meal plan specified.")
            else:
                # Create tabs for each day
                tab_names = [day_display_names[day] for day in available_days]
                day_tabs = st.tabs(tab_names)

                for day_tab, day_key in zip(day_tabs, available_days):
                    with day_tab:
                        try:
                            day_data = weekly_plan[day_key]
                            display_name = day_display_names[day_key]

                            # Validate day_data is a dict
                            if not isinstance(day_data, dict):
                                st.warning(f"Meal data for {display_name} is not in the expected format.")
                                continue

                            # Display day type badge
                            day_type = safe_get_string(day_data, "day_type", "").lower()
                            if day_type == "training":
                                st.markdown(f"""
                                <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px; margin-bottom: 1rem; font-weight: bold;">
                                    🏋️ Training Day
                                </div>
                                """, unsafe_allow_html=True)
                            elif day_type == "rest":
                                st.markdown(f"""
                                <div style="display: inline-block; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 0.5rem 1rem; border-radius: 20px; margin-bottom: 1rem; font-weight: bold;">
                                    🛋️ Rest Day
                                </div>
                                """, unsafe_allow_html=True)

                            # Get meals
                            meals = day_data.get("meals", [])
                            if not isinstance(meals, list):
                                st.warning(f"Meals for {display_name} are not in the expected format.")
                                continue

                            if meals:
                                has_valid_meals = False
                                for i, meal in enumerate(meals, 1):
                                    # Validate each meal is a dict
                                    if not isinstance(meal, dict):
                                        continue

                                    has_valid_meals = True
                                    meal_name = safe_get_string(meal, "name", f"Meal {i}")
                                    foods = meal.get("foods", [])
                                    notes = safe_get_string(meal, "notes", "")
                                    alternatives = meal.get("alternatives", [])

                                    # Display meal card
                                    st.markdown(f"""
                                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #4facfe;">
                                        <h4 style="margin: 0 0 0.5rem 0;">{meal_name}</h4>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Display per-meal nutrition info if available
                                    calories = safe_get_numeric(meal, 'calories')
                                    protein = safe_get_numeric(meal, 'protein_g')
                                    carbs = safe_get_numeric(meal, 'carbs_g')
                                    fats = safe_get_numeric(meal, 'fats_g')

                                    # Display nutrition info if at least calories are available
                                    if calories != 'N/A':
                                        protein_html = f'<span>P: {protein}g</span>' if protein != 'N/A' else ''
                                        carbs_html = f'<span>C: {carbs}g</span>' if carbs != 'N/A' else ''
                                        fats_html = f'<span>F: {fats}g</span>' if fats != 'N/A' else ''

                                        st.markdown(f"""
                                        <div style="background: #e8f5e9; padding: 0.5rem; border-radius: 6px; margin: 0.5rem 0; display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.85rem;">
                                            <span><strong>📊 {calories} cal</strong></span>
                                            {protein_html}
                                            {carbs_html}
                                            {fats_html}
                                        </div>
                                        """, unsafe_allow_html=True)

                                    # Validate foods is a list and display as bullet list
                                    if isinstance(foods, list) and foods:
                                        st.markdown("**Foods:**")
                                        for food in foods:
                                            # Handle non-string food entries
                                            try:
                                                food_str = str(food) if food is not None else "Unknown food"
                                                st.markdown(f"- {food_str}")
                                            except Exception:
                                                st.markdown("- Unknown food")

                                    # Display alternatives if available
                                    if isinstance(alternatives, list) and alternatives:
                                        with st.expander("🔄 Alternative Options"):
                                            for alt in alternatives:
                                                try:
                                                    alt_str = str(alt) if alt is not None else "Alternative option"
                                                    st.markdown(f"- {alt_str}")
                                                except Exception:
                                                    st.markdown("- Alternative option")

                                    # Display notes if present and meaningful
                                    if notes and notes != "Not Specified":
                                        st.caption(f"💡 {notes}")

                                    st.markdown("<br>", unsafe_allow_html=True)

                                if not has_valid_meals:
                                    st.info("No meals specified for this day.")
                            else:
                                st.info("No meals specified for this day.")
                        except Exception as e:
                            st.error(f"Error displaying meals for {display_name}: {str(e)}")
        except Exception as e:
            st.error("Could not display weekly meal plan.")

    elif has_days_plan:
        # Old format (training_day, rest_day, etc.) - maintain backward compatibility
        try:
            st.subheader("📅 Daily Meal Plans")

            days = nutrition_plan["days"]

            # Validate days is a dict before iterating
            if not isinstance(days, dict):
                st.warning("Meal plan days information is not in the expected format.")
            else:
                # Create tabs for all available day types
                day_names = []
                for day_name in days.keys():
                    if day_name == "training_day":
                        day_names.append("Training Day")
                    elif day_name == "rest_day":
                        day_names.append("Rest Day")
                    elif day_name == "weekend_rest_day":
                        day_names.append("Weekend Rest Day")
                    else:
                        day_names.append(day_name.replace('_', ' ').title())

                day_tabs = st.tabs(day_names)

                for day_tab, (day_name, day_data) in zip(day_tabs, days.items()):
                    with day_tab:
                        try:
                            display_name = day_name.replace('_', ' ').title()
                            st.markdown(f"### {display_name}")

                            # Validate day_data is a dict
                            if not isinstance(day_data, dict):
                                st.warning(f"Meal data for {display_name} is not in the expected format.")
                                continue

                            # Validate meals exists and is a list
                            meals = day_data.get("meals", [])
                            if not isinstance(meals, list):
                                st.warning(f"Meals for {display_name} are not in the expected format.")
                                continue

                            if meals:
                                has_valid_meals = False
                                for i, meal in enumerate(meals, 1):
                                    # Validate each meal is a dict
                                    if not isinstance(meal, dict):
                                        continue

                                    has_valid_meals = True
                                    meal_name = safe_get_string(meal, "name", f"Meal {i}")
                                    foods = meal.get("foods", [])
                                    notes = safe_get_string(meal, "notes", "")

                                    # Display meal card
                                    st.markdown(f"""
                                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #4facfe;">
                                        <h4 style="margin: 0 0 0.5rem 0;">{meal_name}</h4>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Display per-meal nutrition info if available
                                    calories = safe_get_numeric(meal, 'calories')
                                    protein = safe_get_numeric(meal, 'protein_g')
                                    carbs = safe_get_numeric(meal, 'carbs_g')
                                    fats = safe_get_numeric(meal, 'fats_g')

                                    # Display nutrition info if at least calories are available
                                    if calories != 'N/A':
                                        protein_html = f'<span>P: {protein}g</span>' if protein != 'N/A' else ''
                                        carbs_html = f'<span>C: {carbs}g</span>' if carbs != 'N/A' else ''
                                        fats_html = f'<span>F: {fats}g</span>' if fats != 'N/A' else ''

                                        st.markdown(f"""
                                        <div style="background: #e8f5e9; padding: 0.5rem; border-radius: 6px; margin: 0.5rem 0; display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.85rem;">
                                            <span><strong>📊 {calories} cal</strong></span>
                                            {protein_html}
                                            {carbs_html}
                                            {fats_html}
                                        </div>
                                        """, unsafe_allow_html=True)

                                    # Validate foods is a list and display as bullet list
                                    if isinstance(foods, list) and foods:
                                        st.markdown("**Foods:**")
                                        for food in foods:
                                            # Handle non-string food entries
                                            try:
                                                food_str = str(food) if food is not None else "Unknown food"
                                                st.markdown(f"- {food_str}")
                                            except Exception:
                                                st.markdown("- Unknown food")

                                    # Display notes if present and meaningful
                                    if notes and notes != "Not Specified":
                                        st.caption(f"💡 {notes}")

                                    st.markdown("<br>", unsafe_allow_html=True)

                                if not has_valid_meals:
                                    st.info("No meals specified for this day type.")
                            else:
                                st.info("No meals specified for this day type.")
                        except Exception as e:
                            st.error(f"Error displaying meals for {day_name}: {str(e)}")
        except Exception as e:
            st.error("Could not display daily meal plans.")

    # Display shopping notes
    shopping_notes = safe_get_string(nutrition_plan, "shopping_notes", "")
    if shopping_notes and shopping_notes != "Not Specified":
        st.subheader("🛒 Shopping Notes")
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
            {shopping_notes}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display adherence notes
    adherence_notes = safe_get_string(nutrition_plan, "adherence_notes", "")
    if adherence_notes and adherence_notes != "Not Specified":
        st.subheader("💪 Adherence Tips")
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
            {adherence_notes}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display batch cooking guide (if exists)
    if "batch_cooking_guide" in nutrition_plan and nutrition_plan["batch_cooking_guide"]:
        batch_cooking_guide = nutrition_plan["batch_cooking_guide"]

        with st.expander("📋 Batch Cooking Guide", expanded=False):
            # Check if batch_cooking_guide is a dict with lists
            if isinstance(batch_cooking_guide, dict):
                try:
                    for recipe_name, instructions in batch_cooking_guide.items():
                        # Format recipe name nicely
                        display_name = recipe_name.replace('_', ' ').title()
                        st.markdown(f"**{display_name}:**")

                        # Check if instructions is a list
                        if isinstance(instructions, list):
                            for instruction in instructions:
                                try:
                                    st.markdown(f"- {str(instruction)}")
                                except Exception:
                                    st.markdown("- (instruction unavailable)")
                        else:
                            # If it's not a list, just display as string
                            try:
                                st.markdown(str(instructions))
                            except Exception:
                                st.markdown("(instructions unavailable)")

                        st.markdown("<br>", unsafe_allow_html=True)
                except Exception as e:
                    # If something goes wrong with dict processing, try displaying as string
                    try:
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
                            {str(batch_cooking_guide)}
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception:
                        st.warning("Batch cooking guide information is not in the expected format.")
            else:
                # If it's a string, display as-is
                try:
                    batch_cooking_str = str(batch_cooking_guide)
                    if batch_cooking_str and batch_cooking_str.strip():
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
                            {batch_cooking_str}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception:
                    st.warning("Batch cooking guide information is not in the expected format.")

    # Display batch cooking note (single field version)
    batch_cooking_note = safe_get_string(nutrition_plan, "batch_cooking_note", "")
    if batch_cooking_note and batch_cooking_note != "Not Specified":
        with st.expander("📋 Batch Cooking Notes", expanded=False):
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
                {batch_cooking_note}
            </div>
            """, unsafe_allow_html=True)

    # View conversation history
    with st.expander("💬 View Consultation Conversation"):
        try:
            messages = get_conversation_history(consultation_id)

            # Validate messages is a list
            if not isinstance(messages, list):
                st.warning("Conversation history is not in the expected format.")
            elif not messages:
                st.info("No conversation history available.")
            else:
                for msg in messages:
                    # Validate each message is a dict with required fields
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        try:
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])
                        except Exception:
                            st.warning("Could not display a message.")
                    else:
                        st.warning("Some messages could not be displayed (invalid format).")
        except Exception as e:
            st.error("Could not load conversation history.")

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

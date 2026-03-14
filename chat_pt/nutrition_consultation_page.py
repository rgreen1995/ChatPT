import streamlit as st
from chat_pt.db_interface import (
    create_consultation,
    save_message,
    get_conversation_history,
    save_nutrition_plan,
)
from chat_pt.llm_handler import LLMHandler
from chat_pt.context_builder import build_consultation_context, build_context_prefix

def render():
    """Render the nutrition consultation page."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🥗 Nutrition Consultation</h1>
        <p style="font-size: 1.1rem; color: #666;">Chat with your AI nutrition coach to create a personalized nutrition plan</p>
    </div>
    """, unsafe_allow_html=True)

    # Show helpful tips in an expandable card for first-time users
    message_count = len(st.session_state.get("messages", []))
    if message_count <= 2:  # Show for first 2 messages
        with st.expander("💡 Tips for a Great Nutrition Consultation", expanded=True):
            st.markdown("""
            **Share these details to get the best personalized plan:**

            - 🎯 **Your Goals:** Fat loss, muscle gain, performance, general health, etc.
            - 🍽️ **Dietary Preferences:** Vegetarian, vegan, keto, flexible, etc.
            - 🚫 **Restrictions/Allergies:** Foods you can't or won't eat
            - ⏰ **Meal Frequency:** How many meals per day do you prefer?
            - 👨‍🍳 **Cooking Time:** How much time can you spend on meal prep?
            - 💰 **Budget:** Any budget constraints?
            - 🏋️ **Training Context:** Your workout schedule (if known from training consultation)

            The AI will ask follow-up questions to ensure your plan is perfect for you!
            """)

    # Display any stored errors
    if "last_error" in st.session_state:
        st.error(st.session_state.last_error["message"])
        with st.expander("Show detailed error"):
            st.code(st.session_state.last_error["traceback"])
        if st.button("Clear Error"):
            del st.session_state.last_error
            st.rerun()

    # Initialize consultation if not exists
    if "nutrition_consultation_id" not in st.session_state:
        st.session_state.nutrition_consultation_id = create_consultation(
            st.session_state.user_id,
            consultation_type='nutrition'
        )
        st.session_state.messages = []
        st.session_state.nutrition_plan = None

        # Build shared context for this user
        context = build_consultation_context(st.session_state.user_id, 'nutrition')

        # Create context-aware initial message
        context_prefix = build_context_prefix(context)

        # Show user what the AI already knows
        if context_prefix:
            st.markdown("""
            <div style="background: #e8f4f8; padding: 1rem; border-radius: 8px; border-left: 4px solid #4facfe; margin: 1rem 0;">
                <h4 style="margin: 0 0 0.5rem 0;">📋 What I Already Know About You</h4>
            </div>
            """, unsafe_allow_html=True)

            # Display context in a nice format
            if context.get('has_profile'):
                st.info(f"**Profile:** {context['shared_profile_summary']}")
            if context.get('has_workout_plan'):
                st.info(f"**Training:** {context['workout_context_summary']}")
            if context.get('has_memory'):
                st.info(f"**Memory:** {context['shared_memory_summary']}")

            st.markdown("<br>", unsafe_allow_html=True)

        # Add initial assistant message
        initial_message = {
            "role": "assistant",
            "content": "Hi! I'm your AI nutrition coach. I'm excited to help you create a personalized nutrition plan that supports your goals! Let's build a plan that fits your lifestyle and helps you succeed. What are your main nutrition goals right now?"
        }
        st.session_state.messages.append(initial_message)
        save_message(st.session_state.nutrition_consultation_id, "assistant", initial_message["content"])

    # Load conversation history if resuming
    if not st.session_state.messages:
        st.session_state.messages = get_conversation_history(st.session_state.nutrition_consultation_id)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Check if nutrition plan was generated - show notification but allow conversation to continue
    if st.session_state.nutrition_plan:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white; margin: 1rem 0;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
            <h3 style="margin: 0.5rem 0; color: white;">Your Nutrition Plan is Ready!</h3>
            <p style="margin: 0; opacity: 0.9;">View your personalized plan or continue chatting to refine it</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🥗 View My Plan", type="primary", use_container_width=True):
                st.session_state.page = "nutrition_plans"
                st.rerun()
        with col2:
            if st.button("🔄 Start New Consultation", use_container_width=True):
                # Reset consultation
                del st.session_state.nutrition_consultation_id
                del st.session_state.messages
                del st.session_state.nutrition_plan
                st.rerun()

        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin: 1rem 0;">
            💬 You can continue chatting to refine your plan or ask questions. Any new plan generated will update the existing one.
        </div>
        """, unsafe_allow_html=True)

    # Check for pre-filled message from plans page
    prefilled = st.session_state.get('prefilled_message', '')
    if prefilled:
        st.info(f"💬 Pre-filled request: {prefilled}")
        if st.button("✅ Send this request", type="primary", use_container_width=True):
            prompt = prefilled
            del st.session_state.prefilled_message
        else:
            st.caption("Or type your own message below")
            prompt = None
    else:
        prompt = None

    # Chat input
    if not prompt:
        prompt = st.chat_input("Type your message here...")

    if prompt:
        # Add user message
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        save_message(st.session_state.nutrition_consultation_id, "user", prompt)

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            # Check if this might be a plan generation request
            plan_keywords = ['create', 'generate', 'plan', 'nutrition', 'meal', 'diet', 'json']
            is_likely_plan_request = any(keyword in prompt.lower() for keyword in plan_keywords)

            spinner_text = "Creating your personalized nutrition plan... This may take a minute ⏳" if is_likely_plan_request else "Thinking..."

            with st.spinner(spinner_text):
                try:
                    # Initialize LLM handler with nutrition mode
                    llm = LLMHandler(provider=st.session_state.llm_provider, mode="nutrition")

                    # Get response
                    response = llm.chat(st.session_state.messages)

                    if not response:
                        st.error("Received empty response from LLM")
                        return

                    # Check if response contains nutrition plan
                    nutrition_plan = llm.extract_nutrition_plan(response, debug=True)

                    # Display the response (but hide JSON blocks if plan was extracted)
                    if nutrition_plan:
                        # Remove JSON code blocks from the response before displaying
                        import re
                        display_response = re.sub(r'```json.*?```', '', response, flags=re.DOTALL | re.IGNORECASE)
                        display_response = re.sub(r'```.*?```', '', display_response, flags=re.DOTALL)

                        # Also remove common JSON-related phrases
                        display_response = re.sub(r'in json format\s*[:\.]?', '', display_response, flags=re.IGNORECASE)
                        display_response = re.sub(r'json format\s*[:\.]?', '', display_response, flags=re.IGNORECASE)
                        display_response = re.sub(r'here\'?s? (the |your )?json', '', display_response, flags=re.IGNORECASE)
                        display_response = re.sub(r'below is (the |your )?json', '', display_response, flags=re.IGNORECASE)

                        # Clean up extra whitespace
                        display_response = re.sub(r'\n\n\n+', '\n\n', display_response.strip())

                        # If very little text remains (mostly JSON), create a nice summary message
                        if len(display_response.strip()) < 50:
                            # Generate a nice message based on the plan
                            calories = nutrition_plan.get('daily_calories', '?')
                            goal = nutrition_plan.get('goal', 'your goals')

                            summary_msg = f"Perfect! I've created your personalized nutrition plan targeting **{calories} calories per day** to support **{goal}**.\n\n"

                            # Add macro overview
                            if 'macros' in nutrition_plan:
                                macros = nutrition_plan['macros']
                                summary_msg += f"**Daily Macros:**\n"
                                summary_msg += f"- Protein: {macros.get('protein_g', '?')}g\n"
                                summary_msg += f"- Carbs: {macros.get('carbs_g', '?')}g\n"
                                summary_msg += f"- Fats: {macros.get('fats_g', '?')}g\n"

                            summary_msg += f"\n✨ Your plan is ready to view! Click **'View My Plan'** below to see the full details."

                            st.markdown(summary_msg)
                            display_response = summary_msg  # Save the clean version
                        else:
                            st.markdown(display_response)

                        # Replace response with cleaned version for saving to history
                        response = display_response
                    else:
                        # No plan extracted, show full response
                        st.markdown(response)

                    # Handle incomplete JSON - auto-retry once
                    if not nutrition_plan and ('```json' in response.lower() or '{' in response):
                        # Check if it looks like truncated JSON
                        json_start = response.find('{')
                        if json_start != -1:
                            potential_json = response[json_start:]
                            if llm.is_json_truncated(potential_json):
                                st.warning("⚠️ Detected incomplete JSON. Requesting completion...")

                                # Auto-retry: ask the LLM to provide just the remaining part
                                retry_prompt = "The previous response was cut off. Please provide the COMPLETE nutrition plan JSON again, but more concisely. Focus only on the essential meal structure and macros."

                                with st.spinner("Requesting complete plan..."):
                                    try:
                                        # Add the retry as a system request (not saved to conversation)
                                        retry_messages = st.session_state.messages.copy()
                                        retry_messages.append({"role": "user", "content": retry_prompt})

                                        retry_response = llm.chat(retry_messages)
                                        nutrition_plan = llm.extract_nutrition_plan(retry_response, debug=True)

                                        if nutrition_plan:
                                            st.success("✅ Received complete nutrition plan!")
                                            # Replace the incomplete response with the complete one
                                            response = retry_response
                                            # Clear the warning and show new response (hide JSON)
                                            st.markdown("---")
                                            import re
                                            retry_display = re.sub(r'```json.*?```', '', retry_response, flags=re.DOTALL | re.IGNORECASE)
                                            retry_display = re.sub(r'```.*?```', '', retry_display, flags=re.DOTALL)
                                            retry_display = re.sub(r'\n\n\n+', '\n\n', retry_display.strip())
                                            if retry_display.strip():
                                                st.markdown(retry_display)
                                            else:
                                                st.markdown("I've created your personalized nutrition plan! 🎉")
                                        else:
                                            st.error("Still couldn't extract complete plan. Please ask me to 'provide a more concise nutrition plan in JSON format'.")
                                    except Exception as retry_error:
                                        st.error(f"Retry failed: {str(retry_error)}")

                    if nutrition_plan:
                        # Save nutrition plan (this will update if one already exists)
                        save_nutrition_plan(
                            st.session_state.user_id,
                            st.session_state.nutrition_consultation_id,
                            nutrition_plan
                        )
                        st.session_state.nutrition_plan = nutrition_plan

                        # Show success message with details
                        calories = nutrition_plan.get('daily_calories', '?')
                        if st.session_state.get('nutrition_plan_previously_generated'):
                            st.success(f"✅ Nutrition plan updated successfully! ({calories} calories/day)")
                        else:
                            st.success(f"✅ Nutrition plan generated successfully! ({calories} calories/day)")
                            st.session_state.nutrition_plan_previously_generated = True

                        # Show a preview of what was detected
                        with st.expander("📋 Detected Plan Summary"):
                            st.write(f"**Daily Calories:** {calories}")
                            if 'macros' in nutrition_plan:
                                macros = nutrition_plan['macros']
                                st.write(f"**Protein:** {macros.get('protein_g', '?')}g")
                                st.write(f"**Carbs:** {macros.get('carbs_g', '?')}g")
                                st.write(f"**Fats:** {macros.get('fats_g', '?')}g")
                            if 'summary' in nutrition_plan:
                                st.write(f"**Summary:** {nutrition_plan['summary'][:200]}...")
                    else:
                        # No plan detected - check if response contains JSON-like content
                        has_json_markers = '```json' in response.lower() or '```' in response or '{' in response

                        if has_json_markers:
                            # Check if JSON looks incomplete (common signs)
                            is_incomplete = (
                                response.rstrip().endswith(',') or
                                response.rstrip().endswith(':') or
                                not response.rstrip().endswith('}')
                            )

                            if is_incomplete:
                                st.error("⚠️ The nutrition plan JSON appears incomplete - the AI response was cut off mid-generation.")
                                st.info("💡 **Solution:** Ask me to provide a more concise plan, or ask for just the meal structure without excessive detail.")

                                with st.expander("Why does this happen?"):
                                    st.markdown("""
                                    The AI has a maximum response length. Very detailed plans can exceed this limit.

                                    **Options:**
                                    1. Ask for "just the meal structure in JSON"
                                    2. Request "a more concise plan with less detail"
                                    3. Get the plan in chunks (macros first, then meals separately)
                                    """)
                            else:
                                st.warning("⚠️ I detected JSON-like content but couldn't extract a valid nutrition plan. The JSON might be missing required fields.")
                                st.info("💡 Please ask me to provide the complete nutrition plan in the correct JSON format.")
                        elif st.session_state.get('nutrition_plan'):
                            # User has a plan but this response doesn't contain one
                            # Check if they're asking for changes
                            change_keywords = ['change', 'update', 'modify', 'adjust', 'swap', 'replace', 'add', 'remove', 'lower', 'higher']
                            if any(word in response.lower() for word in change_keywords):
                                st.info("💡 Tip: If you want to save these changes, ask me to provide the complete updated plan in JSON format!")

                    # Save assistant message
                    assistant_message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(assistant_message)
                    save_message(st.session_state.nutrition_consultation_id, "assistant", response)

                except Exception as e:
                    import traceback
                    error_msg = f"⚠️ Error: {str(e)}\n\nPlease check your API key for {st.session_state.llm_provider}."

                    # Store error in session state so it persists
                    st.session_state.last_error = {
                        "message": error_msg,
                        "traceback": traceback.format_exc()
                    }

                    st.error(error_msg)
                    # Show detailed error in expander for debugging
                    with st.expander("Show detailed error"):
                        st.code(traceback.format_exc())

                    # Don't rerun on error so user can see it
                    return

        st.rerun()

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Consultation Controls")

        if st.button("🔄 Reset Consultation", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_reset"):
                del st.session_state.nutrition_consultation_id
                del st.session_state.messages
                if "nutrition_plan" in st.session_state:
                    del st.session_state.nutrition_plan
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm")

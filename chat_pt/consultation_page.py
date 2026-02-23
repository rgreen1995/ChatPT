import streamlit as st
from chat_pt.database import (
    create_consultation,
    save_message,
    get_conversation_history,
    save_workout_plan,
)
from chat_pt.llm_handler import LLMHandler

def render():
    """Render the consultation page."""
    st.title("💬 Personal Training Consultation")

    # Display any stored errors
    if "last_error" in st.session_state:
        st.error(st.session_state.last_error["message"])
        with st.expander("Show detailed error"):
            st.code(st.session_state.last_error["traceback"])
        if st.button("Clear Error"):
            del st.session_state.last_error
            st.rerun()

    # Initialize consultation if not exists
    if "consultation_id" not in st.session_state:
        st.session_state.consultation_id = create_consultation(st.session_state.user_id)
        st.session_state.messages = []
        st.session_state.workout_plan = None

        # Add initial assistant message
        initial_message = {
            "role": "assistant",
            "content": "Hi! I'm your AI personal trainer. I'm excited to help you create a personalized workout plan! Let's start by understanding your fitness goals. What are you looking to achieve? (e.g., build muscle, lose weight, improve endurance, get stronger)"
        }
        st.session_state.messages.append(initial_message)
        save_message(st.session_state.consultation_id, "assistant", initial_message["content"])

    # Load conversation history if resuming
    if not st.session_state.messages:
        st.session_state.messages = get_conversation_history(st.session_state.consultation_id)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Check if workout plan was generated - show notification but allow conversation to continue
    if st.session_state.workout_plan:
        st.success("✅ Your workout plan has been generated and saved!")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 View My Plan", type="primary", use_container_width=True):
                st.session_state.page = "plans"
                st.rerun()
        with col2:
            if st.button("🔄 Start New Consultation", use_container_width=True):
                # Reset consultation
                del st.session_state.consultation_id
                del st.session_state.messages
                del st.session_state.workout_plan
                st.rerun()

        st.info("💬 You can continue chatting to refine your plan or ask questions. Any new plan generated will update the existing one.")

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        save_message(st.session_state.consultation_id, "user", prompt)

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize LLM handler
                    llm = LLMHandler(provider=st.session_state.llm_provider)

                    # Get response
                    response = llm.chat(st.session_state.messages)

                    if not response:
                        st.error("Received empty response from LLM")
                        return

                    # Check if response contains workout plan
                    workout_plan = llm.extract_workout_plan(response, debug=True)

                    # Display the response
                    st.markdown(response)

                    if workout_plan:
                        # Save workout plan (this will update if one already exists)
                        save_workout_plan(st.session_state.consultation_id, workout_plan)
                        st.session_state.workout_plan = workout_plan

                        # Show success message with details
                        num_days = len(workout_plan.get('schedule', {}))
                        if st.session_state.get('workout_plan_previously_generated'):
                            st.success(f"✅ Workout plan updated successfully! ({num_days} training days)")
                        else:
                            st.success(f"✅ Workout plan generated successfully! ({num_days} training days)")
                            st.session_state.workout_plan_previously_generated = True

                        # Show a preview of what was detected
                        with st.expander("📋 Detected Plan Summary"):
                            st.write(f"**Training days:** {num_days}")
                            st.write(f"**Schedule:** {', '.join(workout_plan.get('schedule', {}).keys())}")
                            if 'summary' in workout_plan:
                                st.write(f"**Summary:** {workout_plan['summary'][:200]}...")
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
                                st.error("⚠️ The workout plan JSON appears incomplete - the AI response was cut off mid-generation.")
                                st.info("💡 **Solution:** Ask me to provide a more concise plan, or ask for just the workout schedule without the detailed nutrition/recovery sections.")

                                with st.expander("Why does this happen?"):
                                    st.markdown("""
                                    The AI has a maximum response length. Very detailed plans can exceed this limit.

                                    **Options:**
                                    1. Ask for "just the workout schedule in JSON"
                                    2. Request "a more concise plan with less detail"
                                    3. Get the plan in chunks (schedule first, then nutrition separately)
                                    """)
                            else:
                                st.warning("⚠️ I detected JSON-like content but couldn't extract a valid workout plan. The JSON might be missing the 'schedule' field.")
                                st.info("💡 Please ask me to provide the complete workout plan in the correct JSON format.")
                        elif st.session_state.get('workout_plan'):
                            # User has a plan but this response doesn't contain one
                            # Check if they're asking for changes
                            change_keywords = ['change', 'update', 'modify', 'adjust', 'swap', 'replace', 'add', 'remove']
                            if any(word in response.lower() for word in change_keywords):
                                st.info("💡 Tip: If you want to save these changes, ask me to provide the complete updated plan in JSON format!")

                    # Save assistant message
                    assistant_message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(assistant_message)
                    save_message(st.session_state.consultation_id, "assistant", response)

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
        st.subheader("Consultation Controls")

        if st.button("🔄 Reset Consultation", type="secondary"):
            if st.session_state.get("confirm_reset"):
                del st.session_state.consultation_id
                del st.session_state.messages
                if "workout_plan" in st.session_state:
                    del st.session_state.workout_plan
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm reset")

        st.markdown("---")
        st.subheader("💡 Tips")
        st.markdown("""
        **Be specific about:**
        - Your fitness goals
        - Training experience
        - Available days per week
        - Equipment access
        - Any injuries or limitations
        - Preferred workout style

        The more detail you provide, the better your personalized plan!
        """)

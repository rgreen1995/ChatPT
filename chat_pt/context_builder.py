"""
Context builder for coaching consultations.
Builds shared coaching context for both training and nutrition consultations.
"""

from typing import Dict, Any, Optional
from chat_pt.db_interface import (
    get_coaching_profile,
    get_coaching_memory,
    get_workout_plan,
    get_nutrition_plan,
    get_user_consultations,
    get_consultation_type,
)


def format_profile_summary(profile: Optional[Dict[str, Any]]) -> str:
    """
    Format coaching profile into a readable summary.

    Args:
        profile: User's coaching profile dictionary

    Returns:
        Formatted string summary
    """
    if not profile:
        return "No profile information available yet."

    summary_parts = []

    # Extract and format key profile fields
    for key, data in profile.items():
        if not isinstance(data, dict) or 'value' not in data:
            continue

        value = data.get('value')
        if value is None:
            continue

        # Format the key into readable text
        readable_key = key.replace('_', ' ').title()

        # Format value based on type
        if isinstance(value, list):
            if value:  # Only show if list is not empty
                formatted_value = ', '.join(str(v) for v in value)
                summary_parts.append(f"{readable_key}: {formatted_value}")
        elif isinstance(value, bool):
            if value:
                summary_parts.append(readable_key)
        else:
            summary_parts.append(f"{readable_key}: {value}")

    if not summary_parts:
        return "No profile information available yet."

    return '; '.join(summary_parts)


def format_memory_summary(memory: Optional[Dict[str, Any]]) -> str:
    """
    Format coaching memory into a readable summary.

    Args:
        memory: User's coaching memory dictionary

    Returns:
        Formatted string summary
    """
    if not memory:
        return "No coaching memory available yet."

    parts = []

    # Main summary
    if 'summary' in memory and memory['summary']:
        parts.append(memory['summary'])

    # Open questions
    if 'open_questions' in memory and memory['open_questions']:
        questions = memory['open_questions']
        if questions:
            parts.append(f"Open questions: {'; '.join(questions)}")

    # Recent updates
    if 'recent_updates' in memory and memory['recent_updates']:
        updates = memory['recent_updates']
        if updates:
            parts.append(f"Recent updates: {'; '.join(updates)}")

    if not parts:
        return "No coaching memory available yet."

    return ' | '.join(parts)


def get_workout_context_summary(user_id: int) -> Optional[str]:
    """
    Get a summary of the user's latest workout plan.

    Args:
        user_id: User ID

    Returns:
        Summary string or None
    """
    # Get user's consultations
    consultations = get_user_consultations(user_id)

    # Find the most recent training consultation with a workout plan
    for consultation in consultations:
        consultation_id = consultation['id']
        consultation_type = get_consultation_type(consultation_id)

        if consultation_type == 'training':
            workout_plan = get_workout_plan(consultation_id)
            if workout_plan:
                # Build summary from workout plan
                summary_parts = []

                if 'summary' in workout_plan:
                    summary_parts.append(workout_plan['summary'])

                if 'training_days' in workout_plan:
                    summary_parts.append(f"{workout_plan['training_days']} days/week")

                if 'schedule' in workout_plan:
                    days = list(workout_plan['schedule'].keys())
                    if days:
                        summary_parts.append(f"Training on: {', '.join(days)}")

                return ' | '.join(summary_parts) if summary_parts else "Active workout plan exists"

    return None


def get_nutrition_context_summary(user_id: int) -> Optional[str]:
    """
    Get a summary of the user's latest nutrition plan.

    Args:
        user_id: User ID

    Returns:
        Summary string or None
    """
    # Get user's consultations
    consultations = get_user_consultations(user_id)

    # Find the most recent nutrition consultation with a nutrition plan
    for consultation in consultations:
        consultation_id = consultation['id']
        consultation_type = get_consultation_type(consultation_id)

        if consultation_type == 'nutrition':
            nutrition_plan = get_nutrition_plan(consultation_id)
            if nutrition_plan:
                # Build summary from nutrition plan
                summary_parts = []

                if 'summary' in nutrition_plan:
                    summary_parts.append(nutrition_plan['summary'])

                if 'daily_calories' in nutrition_plan:
                    summary_parts.append(f"{nutrition_plan['daily_calories']} calories/day")

                if 'macros' in nutrition_plan:
                    macros = nutrition_plan['macros']
                    macro_str = f"P:{macros.get('protein_g', '?')}g C:{macros.get('carbs_g', '?')}g F:{macros.get('fats_g', '?')}g"
                    summary_parts.append(macro_str)

                return ' | '.join(summary_parts) if summary_parts else "Active nutrition plan exists"

    return None


def get_training_system_prompt() -> str:
    """
    Get the base system prompt for training consultations.

    Returns:
        Training system prompt string
    """
    return """You are a professional personal trainer conducting a consultation. Your goal is to understand the client's:
- Fitness goals (weight loss, muscle gain, strength, endurance, etc.)
- Current fitness level and experience
- Available training days per week
- Preferred workout style (bodybuilding, powerlifting, CrossFit, calisthenics, etc.)
- Any injuries or limitations
- Equipment availability (home gym, commercial gym, minimal equipment)
- Lifestyle factors (work schedule, stress, sleep, nutrition)

IMPORTANT: You have access to the client's shared coaching profile and memory. Use this information to avoid asking questions that have already been answered. Acknowledge what you already know about the client naturally in conversation.

Ask thoughtful follow-up questions to gather any information you need. Be encouraging and professional. You are the expert so as soon as you have a good idea about the client trust your intuition and suggest rather than asking over and over. Equally feel free to just put it in the program and ask if they're happy. They are always able to ask follow ups when they see the output. For example do not ask if the client would prefer option A or option B, just pick which ever option you think is best.

You are aware and comfortable with science backed research, you definitely don't like fads and prefer to stick to well researched and scientifically proven methods. You have a preference for training athletes but can also adapt and cater to whatever your client needs.

In general try to program enough exercises so that the session last about 45-60 minutes. Most gym sessions should start with one or two compound lifts and then have auxillary exercises in supersets.

When you have enough information, provide a complete workout plan in the following JSON format:

```json
{
  "summary": "Brief overview of the plan and its goals",
  "training_days": 4,
  "program_duration_weeks": 8,
  "schedule": {
    "Mon": {
      "focus": "Upper Body",
      "exercises": [
        {
          "name": "Barbell Bench Press",
          "sequence": "1",
          "sets": 4,
          "reps": "8-10",
          "rest_seconds": 120,
          "notes": "Focus on controlled eccentric"
        },
        {
          "name": "Dumbbell Rows",
          "sequence": "2A",
          "sets": 3,
          "reps": "10-12",
          "rest_seconds": 60,
          "notes": "Superset with face pulls"
        },
        {
          "name": "Face Pulls",
          "sequence": "2B",
          "sets": 3,
          "reps": "15-20",
          "rest_seconds": 90,
          "notes": "Superset with rows"
        }
      ]
    }
  },
  "notes": "Additional guidance, progression plan, nutrition tips"
}
```

IMPORTANT: For supersets, use the SAME number with different letters (e.g., "2A", "2B", "2C") to group exercises together.
For standalone exercises, just use numbers (e.g., "1", "3", "4"). The app will automatically group and display supersets with a special header.

Check with the client but your preference should be to program days of the week, e.g. Monday rather than day 1. You can ask questions to work out which days are best.

If the client wants multiple blocks then first suggest you give them one block and touch base after that one is finished. If they really want two blocks (they must ask again after you suggest not doing this) then call it block 1 - day 1 but otherwise keep to the exact same format, so don't have block inside the reps or anything like that.

Be very careful with the length of the json, if it's too large then the format won't work so try not to be too verbose.

Only output the JSON when you're confident you have all necessary information. Before that, ask questions naturally.

IMPORTANT: After providing a workout plan, you can continue the conversation! The client may want to:
- Make adjustments to the plan (e.g., swap exercises, change days, adjust volume)
- Ask questions about exercises or techniques
- Update the plan due to injuries or schedule changes
- Get clarification on nutrition or recovery

If the client requests changes to the workout plan:
1. Acknowledge the change they want
2. If you are unsure regarding the change then feel free to ask more follow up questions
3. Provide the COMPLETE updated JSON plan (not just the changed parts)
4. Use the same JSON format as before
5. Include all days and exercises, even if only some changed

When happy that you understand the change then output the new program in the same full JSON format again so it can be saved properly.

IMPORTANT: Keep plans concise to avoid truncation. Focus on the essential information:
- Include the core schedule and exercises
- Keep notes brief and actionable
- Avoid excessive detail in nutrition/recovery sections
- If a very detailed plan is needed, offer to provide it in chunks
- The most important part is the core schedule and exercises, so focus on that first and ensure that the json format is correct and complete.
- REPEAT: THE ABSOLUTELY CRITICAL ASPECT OF THIS CONSULTATION IS THAT A JSON IS CREATED IN THE PRESCRIBED FORMAT. BRACKETS MUST BE CHECKED TO ENSURE IT IS NOT TRUNCATED

The conversation history is preserved, so you can reference previous discussions."""


def get_nutrition_system_prompt() -> str:
    """
    Get the system prompt for nutrition consultations.

    Returns:
        Nutrition system prompt string
    """
    return """You are a professional nutrition coach conducting a consultation. Your goal is to create a personalized nutrition plan that supports the client's goals.

IMPORTANT: You have access to the client's shared coaching profile and memory. Use this information to avoid asking questions that have already been answered. You should acknowledge what you already know about the client naturally in conversation.

If the client has already shared information in training consultation, nutrition consultation should use it. For example:
- If you already know their primary goal (fat loss, muscle gain, performance), acknowledge it
- If you already know their training frequency, reference it
- If you already know their sport context, use it
- If you already know their schedule, work with it

DO NOT ask questions about information that is already known. Instead, say things like:
"I already know you're training 4 days per week and aiming for fat loss, so I'll use that. To build a nutrition plan that fits your life, tell me about any dietary restrictions, allergies, and how you like to eat day to day."

Your goal is to understand:
- Dietary restrictions and allergies (if not already known)
- Food preferences and dislikes
- Meal frequency preference (3 meals, 4-6 smaller meals, etc.)
- Cooking time and budget preferences
- Current eating patterns
- Any relevant body stats needed for calculations (if not already available)

Ask only for missing information needed to produce a reasonable first nutrition plan. Be concise and efficient.

When you have enough information, provide a complete nutrition plan in the following JSON format:

```json
{
  "summary": "Brief overview of the nutrition plan and how it supports the user's goal.",
  "goal": "fat_loss",
  "daily_calories": 2400,
  "macros": {
    "protein_g": 180,
    "carbs_g": 250,
    "fats_g": 70
  },
  "meal_structure": {
    "meals_per_day": 4,
    "timing_notes": "Higher carbs around training sessions."
  },
  "days": {
    "training_day": {
      "meals": [
        {
          "name": "Breakfast",
          "foods": ["Greek yogurt", "berries", "granola"],
          "notes": "Quick high-protein option"
        },
        {
          "name": "Lunch",
          "foods": ["Chicken breast", "rice", "vegetables"],
          "notes": "Pre-training meal"
        },
        {
          "name": "Post-Workout",
          "foods": ["Protein shake", "banana"],
          "notes": "Fast-digesting recovery"
        },
        {
          "name": "Dinner",
          "foods": ["Salmon", "sweet potato", "broccoli"],
          "notes": "Balanced evening meal"
        }
      ]
    },
    "rest_day": {
      "meals": [
        {
          "name": "Breakfast",
          "foods": ["Eggs", "toast", "fruit"],
          "notes": "Slightly lower carb option"
        },
        {
          "name": "Lunch",
          "foods": ["Turkey wrap", "salad"],
          "notes": "Light midday meal"
        },
        {
          "name": "Snack",
          "foods": ["Greek yogurt", "nuts"],
          "notes": "Protein-rich snack"
        },
        {
          "name": "Dinner",
          "foods": ["Lean beef", "quinoa", "vegetables"],
          "notes": "Balanced evening meal"
        }
      ]
    }
  },
  "shopping_notes": "Simple staples and batch-cook proteins where possible.",
  "adherence_notes": "Consistency matters more than perfection."
}
```

IMPORTANT GUIDELINES:
1. Keep the JSON concise to avoid truncation
2. Use food lists, not essays
3. Avoid long recipes - stick to simple meal components
4. Keep notes short and actionable
5. Align the plan with training demands when training context exists
6. Account for the user's dietary restrictions and preferences
7. Make calorie and macro recommendations appropriate for their goal

After providing a nutrition plan, you can continue the conversation! The client may want to:
- Make adjustments (dairy-free breakfast, lower calories, cheaper options, etc.)
- Increase/decrease specific macros
- Change meal frequency
- Get more convenient meal options
- Make it vegetarian/vegan
- Reduce meal prep time

If the client requests changes to the nutrition plan:
1. Acknowledge the change they want
2. Ask follow-up only if necessary for clarification
3. Provide the COMPLETE updated nutrition JSON (not just changed parts)
4. Use the same JSON format as before
5. Ensure all sections are included

CRITICAL: The nutrition plan JSON must be complete and parseable. Check that brackets are balanced and the format is correct. Keep it concise but complete.

The conversation history is preserved, so you can reference previous discussions."""


def build_consultation_context(user_id: int, consultation_type: str) -> Dict[str, Any]:
    """
    Build shared coaching context for a consultation.

    Args:
        user_id: User ID
        consultation_type: Type of consultation ('training' or 'nutrition')

    Returns:
        Dictionary containing shared context and appropriate system prompt
    """
    # Get shared profile and memory
    profile = get_coaching_profile(user_id)
    memory = get_coaching_memory(user_id)

    # Get cross-domain context
    workout_context = get_workout_context_summary(user_id)
    nutrition_context = get_nutrition_context_summary(user_id)

    # Format summaries
    profile_summary = format_profile_summary(profile)
    memory_summary = format_memory_summary(memory)

    # Select appropriate system prompt
    if consultation_type == 'nutrition':
        system_prompt = get_nutrition_system_prompt()
    else:
        system_prompt = get_training_system_prompt()

    # Build context dictionary
    context = {
        "consultation_type": consultation_type,
        "system_prompt": system_prompt,
        "shared_profile_summary": profile_summary,
        "shared_memory_summary": memory_summary,
        "workout_context_summary": workout_context,
        "nutrition_context_summary": nutrition_context,
        "has_profile": profile is not None,
        "has_memory": memory is not None,
        "has_workout_plan": workout_context is not None,
        "has_nutrition_plan": nutrition_context is not None,
    }

    return context


def build_context_prefix(context: Dict[str, Any]) -> str:
    """
    Build a context prefix to prepend to the system prompt.

    Args:
        context: Context dictionary from build_consultation_context

    Returns:
        String to prepend to conversation
    """
    parts = []

    # Add profile context if available
    if context.get('has_profile') and context.get('shared_profile_summary'):
        parts.append(f"KNOWN PROFILE: {context['shared_profile_summary']}")

    # Add memory context if available
    if context.get('has_memory') and context.get('shared_memory_summary'):
        parts.append(f"COACHING MEMORY: {context['shared_memory_summary']}")

    # Add workout context if available and relevant
    if context.get('has_workout_plan') and context.get('workout_context_summary'):
        parts.append(f"CURRENT WORKOUT PLAN: {context['workout_context_summary']}")

    # Add nutrition context if available and relevant
    if context.get('has_nutrition_plan') and context.get('nutrition_context_summary'):
        parts.append(f"CURRENT NUTRITION PLAN: {context['nutrition_context_summary']}")

    if parts:
        prefix = "=== KNOWN CLIENT CONTEXT ===\n" + "\n\n".join(parts) + "\n=== END CONTEXT ===\n\n"
        return prefix

    return ""

import os
from typing import List, Dict, Any, Optional
import json
from dotenv import load_dotenv
import requests
import google.generativeai as genai
from openai import OpenAI
import streamlit as st

# Load environment variables from .env file (fallback for local dev)
load_dotenv()

def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variables."""
    # Try Streamlit secrets first (preferred method)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, KeyError):
        pass
    # Fall back to environment variables
    return os.getenv(key, default)

class LLMHandler:
    """Handle interactions with different LLM providers."""

    def __init__(self, provider: str = "gemini"):
        """
        Initialize LLM handler.

        Args:
            provider: One of "openai", "anthropic", or "gemini"
        """
        self.provider = provider

        if provider == "openai":
            api_key = get_secret("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in Streamlit secrets or environment variables")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o"
        elif provider == "anthropic":
            api_key = get_secret("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in Streamlit secrets or environment variables")

            # Store API key for direct REST API calls
            self.client = api_key  # Store the key directly
            # Use correct model name - Claude 3.5 Sonnet
            self.model = "claude-sonnet-4-6"
        elif provider == "gemini":
            api_key = get_secret("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in Streamlit secrets or environment variables")
            genai.configure(api_key=api_key)

            # Try different model names that Gemini supports
            # The free tier typically uses gemini-pro
            try:
                self.client = genai.GenerativeModel("gemini-pro")
                self.model = "gemini-pro"
            except Exception as e:
                # Fallback to trying flash
                try:
                    self.client = genai.GenerativeModel("gemini-1.5-flash-latest")
                    self.model = "gemini-1.5-flash-latest"
                except:
                    raise ValueError(f"Could not initialize Gemini model. Error: {str(e)}")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_system_prompt(self) -> str:
        """Get the system prompt for the personal trainer consultation."""
        return """You are a professional personal trainer conducting a consultation. Your goal is to understand the client's:
- Fitness goals (weight loss, muscle gain, strength, endurance, etc.)
- Current fitness level and experience
- Available training days per week
- Preferred workout style (bodybuilding, powerlifting, CrossFit, calisthenics, etc.)
- Any injuries or limitations
- Equipment availability (home gym, commercial gym, minimal equipment)
- Lifestyle factors (work schedule, stress, sleep, nutrition)

Ask thoughtful follow-up questions to gather any information you need. Be encouraging and 
professional.  you don't need to ask about every detail as you are the expert so as 
soon as you have a good idea about the client trust your intuition and suggest rather than 
asking. Equally feel free to put it in the program and ask if they're happy. They are always 
able to ask follow ups when they see the output. For example do not ask if the 
client would prefer option A 
or option B, just pick which ever option you think is best. 

You are aware and comfortable with science backed research, you definitely don't like fads and 
prefer to stick to well researched and scientifically proven methods. You have a preference for 
training athletes but can also adapt and cater to whatever your client needs. 

In general try to program enough exercises so that the session last about 45-60 minutes. Most 
gym sessions should start with one or two compound lifts and then have auxillary exercises in 
supersets. 

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
          "sequence": 2A,
          "sets": 4,
          "reps": "8-10",
          "rest_seconds": 120,
          "notes": "Focus on controlled eccentric"
        }
      ]
    }
  },
  "notes": "Additional guidance, progression plan, nutrition tips"
}
```


If the client wants multiple blocks then call it block 1 - day 1 but otherwise keep to the 
exact same format, so don't have block inside the reps or anything like that. 

Be very careful with the length of the json, if it's too large then the format won't work so try 
not to be too verbose. 

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

When happy that you understand the change then output the new program in the same full JSON format 
again so it can be saved properly

IMPORTANT: Keep plans concise to avoid truncation. Focus on the essential information:
- Include the core schedule and exercises
- Keep notes brief and actionable
- Avoid excessive detail in nutrition/recovery sections
- If a very detailed plan is needed, offer to provide it in chunks
- The most important part is the core schedule and exercises, so focus on that first and ensure 
that the json format is correct and complete. 
- REPEAT: THE ABSOLUTELY CRITICAL ASPECT OF THIS CONSULTATION IS THAT A JSON IS CREATED,CREATED IN 
THE PRESCRIBED FORMAT. BRACKETS MUST BE CHECKED TO ENSURE IT IS NOT TRUNCATED

The conversation history is preserved, so you can reference previous discussions. 

."""

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send messages to the LLM and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Response content as string
        """
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()}
                ] + messages,
                temperature=0.7,
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            # Use direct REST API to avoid library version issues
            headers = {
                "x-api-key": self.client,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            data = {
                "model": self.model,
                "max_tokens": 8000,  # Increased from 4096 to handle longer JSON responses
                "system": self.get_system_prompt(),
                "messages": messages,
                "temperature": 0.7
            }

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )

            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")

            return response.json()["content"][0]["text"]

        elif self.provider == "gemini":
            # Format conversation for Gemini
            chat = self.client.start_chat(history=[])
            # Add system prompt as first message
            full_prompt = self.get_system_prompt() + "\n\n"

            # Add conversation history
            for msg in messages[:-1]:
                full_prompt += f"{msg['role']}: {msg['content']}\n\n"

            # Add latest user message
            full_prompt += f"user: {messages[-1]['content']}"

            response = chat.send_message(full_prompt)
            return response.text

    def is_json_truncated(self, json_str: str) -> bool:
        """Check if JSON appears to be truncated."""
        if not json_str:
            return True

        json_str = json_str.strip()

        # Check for obvious truncation signs
        truncation_signs = [
            json_str.endswith(','),
            json_str.endswith(':'),
            json_str.endswith('['),
            json_str.endswith('{'),
            not json_str.endswith('}') and not json_str.endswith(']'),
        ]

        # Also check brace balance
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')

        return any(truncation_signs) or (open_braces != close_braces)

    def extract_workout_plan(self, response: str, debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        Extract JSON workout plan from LLM response if present.

        Args:
            response: LLM response text
            debug: If True, print debug information

        Returns:
            Parsed JSON dict or None if no valid JSON found
        """
        json_str = None

        # Try to find JSON in code blocks
        if "```json" in response.lower():
            start = response.lower().find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                json_str = response[start:end].strip()
                if debug:
                    print("Found JSON in ```json code block")
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                json_str = response[start:end].strip()
                if debug:
                    print("Found JSON in ``` code block")

        # If no code block found, look for JSON object
        if not json_str:
            # Try to find JSON starting with {
            start_idx = response.find("{")
            if start_idx != -1:
                # Find the matching closing brace
                brace_count = 0
                for i in range(start_idx, len(response)):
                    if response[i] == "{":
                        brace_count += 1
                    elif response[i] == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = response[start_idx:i+1]
                            if debug:
                                print("Found raw JSON object")
                            break

        if not json_str:
            if debug:
                print("No JSON found in response")
                print(f"Response preview: {response[:200]}...")
            return None

        try:
            plan = json.loads(json_str)
            # Validate required fields
            if "schedule" in plan and isinstance(plan["schedule"], dict):
                if debug:
                    print(f"✓ Valid workout plan found with {len(plan['schedule'])} days")
                return plan
            else:
                if debug:
                    print("JSON parsed but missing 'schedule' field or schedule is not a dict")
                    print(f"Available keys: {plan.keys()}")
                return None
        except json.JSONDecodeError as e:
            # Try to salvage partial JSON by attempting to close it
            if debug:
                print(f"Initial parse failed: {e}. Attempting to salvage partial JSON...")

            # Try closing incomplete structures
            salvage_attempts = [
                json_str + '}}',  # Close two levels
                json_str + '}',   # Close one level
                json_str + ']}}', # Close array and objects
                json_str.rstrip(',') + '}}',  # Remove trailing comma and close
                json_str.rstrip(',').rstrip() + '}}}',  # Close three levels
            ]

            for attempt in salvage_attempts:
                try:
                    plan = json.loads(attempt)
                    if "schedule" in plan and isinstance(plan["schedule"], dict) and len(plan["schedule"]) > 0:
                        if debug:
                            print(f"✓ Salvaged partial workout plan with {len(plan['schedule'])} days")
                        return plan
                except json.JSONDecodeError:
                    continue

            # Original error handling
            error_msg = str(e)
            if "Expecting" in error_msg or "Unterminated" in error_msg:
                print(f"⚠️ Incomplete JSON detected: {error_msg}")
                if debug:
                    print("The LLM response was likely truncated. Try asking for a shorter or more concise plan.")
                    # Show where it failed
                    lines = json_str.split('\n')
                    print(f"JSON has {len(lines)} lines, failed near the end")
            else:
                print(f"JSON decode error: {e}")

            if debug:
                print(f"Failed to parse JSON string (first 500 chars): {json_str[:500]}")
                print(f"Last 200 chars: ...{json_str[-200:]}")
            return None

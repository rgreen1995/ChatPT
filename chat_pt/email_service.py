"""
Email service for ChatPT using Resend.
Sends welcome emails and other notifications.
"""

import os
import streamlit as st

def get_secret(key: str, default: str = None) -> str:
    """Get secret from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, KeyError):
        pass
    return os.getenv(key, default)


def is_email_configured() -> bool:
    """Check if email service is configured."""
    api_key = get_secret("RESEND_API_KEY")
    return bool(api_key)


def send_welcome_email(email: str, name: str) -> bool:
    """
    Send a welcome email to a new user.

    Args:
        email: User's email address
        name: User's name

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not is_email_configured():
        return False

    try:
        import resend

        api_key = get_secret("RESEND_API_KEY")
        from_email = get_secret("RESEND_FROM_EMAIL", "ChatPT <onboarding@chatpt.app>")

        resend.api_key = api_key

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 14px;
                }}
                .emoji {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="emoji">💪</div>
                <h1>Welcome to ChatPT!</h1>
            </div>
            <div class="content">
                <h2>Hi {name}!</h2>
                <p>Thank you for joining ChatPT - your AI-powered personal trainer!</p>

                <p>We're excited to help you achieve your fitness goals. Here's what you can do with ChatPT:</p>

                <ul>
                    <li><strong>🎯 Get Personalized Workout Plans</strong> - Chat with our AI trainer to create a custom program tailored to your goals</li>
                    <li><strong>📊 Track Your Progress</strong> - Log your workouts and visualize your improvements over time</li>
                    <li><strong>💬 Continuous Support</strong> - Ask questions and adjust your plan anytime through the AI chat</li>
                    <li><strong>🏋️ Detailed Exercise Guidance</strong> - Get complete workout schedules with sets, reps, and rest periods</li>
                </ul>

                <h3>Ready to Get Started?</h3>
                <ol>
                    <li>Log in to your account</li>
                    <li>Start a new consultation</li>
                    <li>Tell us about your fitness goals and experience</li>
                    <li>Get your personalized workout plan in minutes!</li>
                </ol>

                <div style="text-align: center;">
                    <a href="https://chatpt.streamlit.app" class="button">Start Your First Consultation</a>
                </div>

                <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #666; font-size: 14px;">
                    <strong>Need help?</strong> Reply to this email or check out our documentation to learn more about ChatPT.
                </p>
            </div>
            <div class="footer">
                <p>ChatPT - Your AI-Powered Personal Trainer</p>
                <p>You received this email because you signed up for a ChatPT account.</p>
            </div>
        </body>
        </html>
        """

        params = {
            "from": from_email,
            "to": [email],
            "subject": f"Welcome to ChatPT, {name}! 💪",
            "html": html_content,
        }

        response = resend.Emails.send(params)
        print(f"✅ Email sent successfully: {response}")
        return True

    except Exception as e:
        # Log error but don't fail signup if email fails
        print(f"❌ Failed to send welcome email: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_plan_ready_email(email: str, name: str, plan_details: str = "") -> bool:
    """
    Send an email notification when a workout plan is ready.

    Args:
        email: User's email address
        name: User's name
        plan_details: Brief description of the plan

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not is_email_configured():
        return False

    try:
        import resend

        api_key = get_secret("RESEND_API_KEY")
        from_email = get_secret("RESEND_FROM_EMAIL", "ChatPT <notifications@chatpt.app>")

        resend.api_key = api_key

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✅ Your Workout Plan is Ready!</h1>
            </div>
            <div class="content">
                <h2>Hi {name}!</h2>
                <p>Great news! Your personalized workout plan has been generated and is ready to view.</p>

                {f"<p><strong>Plan Summary:</strong> {plan_details}</p>" if plan_details else ""}

                <p>Your plan includes:</p>
                <ul>
                    <li>Complete workout schedule</li>
                    <li>Detailed exercise instructions</li>
                    <li>Sets, reps, and rest periods</li>
                    <li>Progression guidance</li>
                </ul>

                <div style="text-align: center;">
                    <a href="https://chatpt.streamlit.app" class="button">View Your Plan</a>
                </div>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    Remember: You can always chat with your AI trainer to make adjustments or ask questions!
                </p>
            </div>
        </body>
        </html>
        """

        params = {
            "from": from_email,
            "to": [email],
            "subject": "✅ Your ChatPT Workout Plan is Ready!",
            "html": html_content,
        }

        resend.Emails.send(params)
        return True

    except Exception as e:
        print(f"Failed to send plan ready email: {str(e)}")
        return False

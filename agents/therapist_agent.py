from services.gemini_service import call_gemini
from prompts.templates import THERAPIST_PROMPT

def generate_therapeutic_guidance(user_message, emotion):
    """
    Generates CBT-based advice and therapeutic strategy for the given message and emotion.
    """
    user_prompt = f"""User Message: {user_message}
Detected Emotion: {emotion}

Please generate CBT validation, reframing, and stress-management guidance for this situation.
"""
    try:
        guidance = call_gemini(THERAPIST_PROMPT, user_prompt, temperature=0.6, max_tokens=150)
        return guidance
    except Exception as e:
        return f"Focus on gentle validation, pacing, and basic CBT grounding techniques. (Error generating guide: {str(e)})"

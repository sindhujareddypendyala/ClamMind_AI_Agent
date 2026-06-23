from services.gemini_service import call_gemini
from prompts.templates import EMOTION_DETECTOR_PROMPT

def detect_emotion(user_message):
    """
    Analyzes user message and returns the detected emotion as a string.
    """
    try:
        response = call_gemini(EMOTION_DETECTOR_PROMPT, f"User Message: {user_message}", temperature=0.1, max_tokens=10)
        emotion = response.strip().lower()
        
        # Validate that the emotion is in our target list
        valid_emotions = ["anxious", "stressed", "sad", "angry", "tired", "overwhelmed", "lonely", "happy", "calm", "neutral"]
        for e in valid_emotions:
            if e in emotion:
                return e
        
        return "neutral"
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return "neutral"

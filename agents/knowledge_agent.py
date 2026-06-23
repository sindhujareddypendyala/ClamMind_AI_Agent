import os
import json

KB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "knowledge_base", "mental_health.json")

def get_wellness_guidance(emotion: str):
    """
    Retrieves guidance from mental_health.json matching the emotion.
    Normalizes emotion names (e.g. anxious -> anxiety, stressed -> stress, sad -> sadness).
    """
    # Map emotions from emotion detector to JSON knowledge base keys
    mapping = {
        "stressed": "stress",
        "anxious": "anxiety",
        "sad": "sadness",
        "overwhelmed": "burnout",
        "tired": "sleep",
        "lonely": "sadness",
        "happy": "motivation",
        "neutral": "stress",
        "stress": "stress",
        "anxiety": "anxiety",
        "sadness": "sadness",
        "burnout": "burnout",
        "overthinking": "overthinking",
        "sleep": "sleep",
        "confidence": "confidence",
        "motivation": "motivation"
    }
    
    key = mapping.get(emotion.lower(), "stress")
    
    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            kb = json.load(f)
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return {
            "description": "General wellness guidance.",
            "exercise": "16s Box Breathing",
            "affirmation": "I choose to be present and breathe.",
            "tips": ["Breathe slowly.", "Take a micro-break."]
        }
        
    if key in kb:
        return kb[key]
    return kb.get("stress")

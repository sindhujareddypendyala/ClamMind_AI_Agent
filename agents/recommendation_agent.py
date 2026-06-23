import database.db_manager as db
from agents.knowledge_agent import get_wellness_guidance

def get_recommendations(user_id: int, emotion: str):
    """
    Upgraded Recommendation Agent.
    Uses: Emotion + Knowledge Base + Mood History
    Generates tailored exercises and plan recommendations.
    """
    emotion = emotion.lower().strip()
    kb_guidance = get_wellness_guidance(emotion)
    
    # Fetch mood logs history
    mood_logs = db.get_mood_logs(user_id, days=7)
    recent_stress_levels = [log['stress_level'] for log in mood_logs]
    recent_anxiety_levels = [log['anxiety_level'] for log in mood_logs]
    
    avg_recent_stress = sum(recent_stress_levels) / len(recent_stress_levels) if recent_stress_levels else 0
    avg_recent_anxiety = sum(recent_anxiety_levels) / len(recent_anxiety_levels) if recent_anxiety_levels else 0
    
    # 1. Determine Breathing Exercise
    if emotion in ["anxious", "anxiety"]:
        breathing_exercise = "Calm Breathing"
    elif emotion in ["stressed", "stress", "overwhelmed"]:
        breathing_exercise = "Box Breathing"
    elif emotion in ["tired", "sleep"]:
        breathing_exercise = "4-7-8 Breathing"
    else:
        breathing_exercise = "Deep Breathing"
        
    # 2. Determine Wellness Exercise
    if emotion in ["anxious", "anxiety", "overthinking"]:
        wellness_exercise = "Grounding Exercise"
    elif emotion in ["sad", "sadness", "lonely"]:
        wellness_exercise = "Gratitude Exercise"
    elif emotion in ["happy", "calm", "neutral"]:
        wellness_exercise = "Confidence Exercise"
    else:
        wellness_exercise = "PMR (Progressive Muscle Relaxation)"
        
    # 3. Determine Wellness Plan Type
    if avg_recent_stress > 6 or emotion in ["stressed", "stress"]:
        wellness_plan_type = "Stress Recovery Plan"
    elif emotion in ["overwhelmed", "burnout"]:
        wellness_plan_type = "Burnout Recovery Plan"
    elif emotion in ["tired", "sleep"]:
        wellness_plan_type = "Sleep Improvement Plan"
    elif emotion in ["sad", "sadness", "lonely", "confidence"]:
        wellness_plan_type = "Confidence Building Plan"
    else:
        wellness_plan_type = "Weekly Wellness Plan"
        
    # 4. Sleep Recommendation
    sleep_recommendation = "Practice 4-7-8 breathing and dim screens 1 hour before bed."
    if avg_recent_anxiety > 6:
        sleep_recommendation = "Journal worries to dump thoughts before sleeping."
        
    # 5. Confidence Exercise
    confidence_exercise = "Write down 3 personal achievements or strengths today."
    
    explanation = f"Based on feeling {emotion} and your recent weekly logs (Stress: {round(avg_recent_stress, 1)}/10), we suggest this specific wellness combination to calm your thoughts."
    
    return {
        "breathing_exercise": breathing_exercise,
        "wellness_exercise": wellness_exercise,
        "wellness_plan_type": wellness_plan_type,
        "sleep_recommendation": sleep_recommendation,
        "confidence_exercise": confidence_exercise,
        "explanation": explanation,
        "kb_description": kb_guidance.get("description", ""),
        "kb_affirmation": kb_guidance.get("affirmation", ""),
        "kb_tips": kb_guidance.get("tips", [])
    }

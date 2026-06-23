def get_recommendations(emotion):
    """
    Determines breathing exercise, mindfulness/wellness exercise, and wellness plan
    recommendations based on the user's primary emotional state.
    """
    emotion = emotion.lower().strip()
    
    # Supported Exercises:
    # Breathing: Deep Breathing, Box Breathing, 4-7-8 Breathing, Calm Breathing
    # Mindfulness: Grounding Exercise, Gratitude Exercise, Confidence Exercise, Sleep Relaxation Exercise
    # Plans: Stress Recovery Plan, Anxiety Recovery Plan, Sleep Improvement Plan, Confidence Building Plan, Focus Improvement Plan
    
    recommendations = {
        "anxious": {
            "breathing_exercise": "4-7-8 Breathing",
            "wellness_exercise": "Grounding Exercise",
            "wellness_plan_type": "Anxiety Recovery Plan",
            "explanation": "This combination activates your parasympathetic nervous system, slowing your heart rate and grounding your mind."
        },
        "stressed": {
            "breathing_exercise": "Box Breathing",
            "wellness_exercise": "Grounding Exercise",
            "wellness_plan_type": "Stress Recovery Plan",
            "explanation": "Box breathing is used by professionals to regain composure, while grounding anchors your attention away from stressors."
        },
        "overwhelmed": {
            "breathing_exercise": "Box Breathing",
            "wellness_exercise": "Grounding Exercise",
            "wellness_plan_type": "Stress Recovery Plan",
            "explanation": "When overwhelmed, taking structured holds with Box breathing helps clear mental clutter and restore focus."
        },
        "sad": {
            "breathing_exercise": "Deep Breathing",
            "wellness_exercise": "Gratitude Exercise",
            "wellness_plan_type": "Confidence Building Plan",
            "explanation": "Deep breaths increase oxygen flow, and a brief gratitude check-in helps shift perspective towards positive thoughts."
        },
        "lonely": {
            "breathing_exercise": "Deep Breathing",
            "wellness_exercise": "Gratitude Exercise",
            "wellness_plan_type": "Confidence Building Plan",
            "explanation": "Nurturing gratitude helps bring comfort, and deep breathing releases tension when feeling isolated."
        },
        "angry": {
            "breathing_exercise": "Box Breathing",
            "wellness_exercise": "Grounding Exercise",
            "wellness_plan_type": "Stress Recovery Plan",
            "explanation": "Regulate intense spikes in heart rate through Box breathing, and ground yourself in the physical room to cool down."
        },
        "tired": {
            "breathing_exercise": "Calm Breathing",
            "wellness_exercise": "Sleep Relaxation Exercise",
            "wellness_plan_type": "Sleep Improvement Plan",
            "explanation": "Calm, gentle pacing aligns your body for restorative rest, preparing you for sleep relaxation."
        },
        "happy": {
            "breathing_exercise": "Calm Breathing",
            "wellness_exercise": "Confidence Exercise",
            "wellness_plan_type": "Focus Improvement Plan",
            "explanation": "Harness this positive energy to build confidence or direct your focus towards meaningful goals."
        },
        "calm": {
            "breathing_exercise": "Calm Breathing",
            "wellness_exercise": "Confidence Exercise",
            "wellness_plan_type": "Focus Improvement Plan",
            "explanation": "Being calm is the perfect time to build self-affirmation and outline your plans for focus."
        },
        "neutral": {
            "breathing_exercise": "Deep Breathing",
            "wellness_exercise": "Confidence Exercise",
            "wellness_plan_type": "Focus Improvement Plan",
            "explanation": "Ground yourself with deep breathing and reinforce your self-confidence to proceed with clarity."
        }
    }
    
    # Default fallback
    return recommendations.get(emotion, recommendations["neutral"])

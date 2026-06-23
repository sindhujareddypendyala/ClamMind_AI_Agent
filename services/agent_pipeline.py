from agents.domain_guard import check_domain
from agents.emotion_detector import detect_emotion
from agents.memory_manager import get_context_memory
from agents.therapist_agent import generate_therapeutic_guidance
from agents.mood_prediction_agent import get_mood_pipeline_context
from agents.recommendation_agent import get_recommendations
from services.gemini_service import call_gemini
from prompts.templates import SYNTHESIS_PROMPT

def run_agent_pipeline(user_id, conversation_id, user_message):
    """
    Executes the entire Multi-Agent pipeline:
    1. Domain Guard Check
    2. Emotion Detection
    3. Memory assembly
    4. Therapist guidance generation
    5. Mood history context gathering
    6. Recommendation selection
    7. Gemini synthesis into the final 150-word response
    
    Returns: A dictionary with 'content', 'emotion', 'exercises', 'plan', 'blocked'.
    """
    # 1. Domain Guard Check
    is_allowed, block_response = check_domain(user_message)
    if not is_allowed:
        return {
            "content": block_response,
            "emotion": "neutral",
            "exercises": None,
            "plan": None,
            "blocked": True
        }
    
    # 2. Emotion Detection
    emotion = detect_emotion(user_message)
    
    # 3. Memory Assembly
    memory_context = get_context_memory(user_id, conversation_id)
    
    # 4. Therapist Guidance (CBT Strategy)
    therapist_guidance = generate_therapeutic_guidance(user_message, emotion)
    
    # 5. Mood History Context
    mood_context = get_mood_pipeline_context(user_id)
    
    # 6. Recommendations
    recs = get_recommendations(emotion)
    
    # 7. Gemini Synthesis
    user_prompt = f"""
Current User Message: "{user_message}"
Detected Emotion: {emotion}

Memory Context:
{memory_context}

Recent Mood logs Context:
{mood_context}

Therapist Guidance:
{therapist_guidance}

Recommendation Agent Suggestions:
- Breathing Exercise: {recs['breathing_exercise']}
- Wellness Exercise: {recs['wellness_exercise']}
- Plan: {recs['wellness_plan_type']}
- Rationale: {recs['explanation']}

Please synthesize these inputs and write the final response to the user following the response format constraints.
"""
    
    try:
        final_response = call_gemini(SYNTHESIS_PROMPT, user_prompt, temperature=0.7, max_tokens=150)
    except Exception as e:
        final_response = (
            f"I hear you. Feeling {emotion} can be really tough, and it's completely okay to feel this way. "
            "Let's slow things down together. Try taking a few deep breaths and focusing only on the next small step. "
            f"If you'd like, we can try a gentle {recs['breathing_exercise']} breathing exercise together. "
            "What's been weighing on your mind the most lately?"
        )

    return {
        "content": final_response,
        "emotion": emotion,
        "exercises": {
            "breathing": recs['breathing_exercise'],
            "wellness": recs['wellness_exercise']
        },
        "plan": recs['wellness_plan_type'],
        "blocked": False
    }

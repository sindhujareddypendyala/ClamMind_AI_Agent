from agents.domain_guard import check_domain
from agents.emotion_detector import detect_emotion
from agents.memory_manager import get_context_memory
from agents.therapist_agent import generate_therapeutic_guidance
from agents.mood_prediction_agent import get_mood_pipeline_context
from agents.knowledge_agent import get_wellness_guidance
from agents.recommendation_agent import get_recommendations
from agents.wellness_planner_agent import DESCRIPTIONS as PLAN_DESCRIPTIONS
from services.gemini_service import call_gemini
from prompts.templates import SYNTHESIS_PROMPT

def run_agent_pipeline(user_id, conversation_id, user_message):
    """
    Executes the upgraded Multi-Agent pipeline:
    1. Domain Guard Check
    2. Emotion Detection
    3. Memory assembly
    4. Therapist guidance generation
    5. Mood history context gathering
    6. Knowledge Base retrieval (Knowledge Base Agent)
    7. Recommendation selection (Emotion + Knowledge Base + Mood History)
    8. Gemini (Groq Llama 3.1) Synthesis
    
    Returns: A dictionary with 'content', 'emotion', 'exercises', 'plan', 'blocked', 'suggestions'.
    """
    # 1. Domain Guard Check
    is_allowed, block_response = check_domain(user_message)
    if not is_allowed:
        return {
            "content": block_response,
            "emotion": "neutral",
            "exercises": None,
            "plan": None,
            "blocked": True,
            "suggestions": ["Mood Tracker"]
        }
    
    # 2. Emotion Detection
    emotion = detect_emotion(user_message)
    
    # 3. Memory Assembly
    memory_context = get_context_memory(user_id, conversation_id)
    
    # 4. Therapist Guidance (CBT Strategy)
    therapist_guidance = generate_therapeutic_guidance(user_message, emotion, memory_context)
    
    # 5. Mood History Context
    mood_context = get_mood_pipeline_context(user_id)
    
    # 6. Knowledge Base guidance
    kb_guidance = get_wellness_guidance(emotion)
    
    # 7. Recommendations
    recs = get_recommendations(user_id, emotion)
    
    # 8. Plan Context
    plan_title = recs['wellness_plan_type']
    plan_desc = PLAN_DESCRIPTIONS.get(plan_title, "Personalized wellness plan.")
    
    # Assemble synthesis prompt
    user_prompt = f"""
Current User Message: "{user_message}"
Detected Emotion: {emotion}

Memory Context:
{memory_context}

Recent Mood logs Context:
{mood_context}

Therapist Guidance Strategy:
{therapist_guidance}

Knowledge Base Guidelines:
- Description: {kb_guidance.get('description')}
- Affirmation: {kb_guidance.get('affirmation')}
- Tips: {", ".join(kb_guidance.get('tips', []))}

Recommendations:
- Breathing Exercise: {recs['breathing_exercise']}
- Wellness Exercise: {recs['wellness_exercise']}
- Recommended Plan: {recs['wellness_plan_type']} ({plan_desc})
- Sleep Recommendation: {recs['sleep_recommendation']}
- Confidence Exercise: {recs['confidence_exercise']}
- Rationale: {recs['explanation']}

Please synthesize these inputs and write the final response to the user. Strictly follow the word capping (80-120 words) and structure rules (Empathy, Guidance, Exercise, Follow-up Question).
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

    # Dynamic suggestions for the frontend buttons
    suggestions = ["Breathing Exercise", "Recovery Plan", "Mood Tracker"]

    return {
        "content": final_response,
        "emotion": emotion,
        "exercises": {
            "breathing": recs['breathing_exercise'],
            "wellness": recs['wellness_exercise']
        },
        "plan": recs['wellness_plan_type'],
        "blocked": False,
        "suggestions": suggestions
    }

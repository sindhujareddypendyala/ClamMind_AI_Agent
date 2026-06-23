import json
import database.db_manager as db
from services.gemini_service import call_gemini

STATE_TRACKER_PROMPT = """You are the Conversation State Tracker for CalmMind AI.
Your job is to analyze the conversation state (topic, emotion, and stage) based on the latest user message, previous state, and recent history.

You must respond with a JSON object. The response must contain exactly these keys:
{
  "current_topic": "e.g. students, exams, parents, work, future, sleep, or general",
  "current_emotion": "e.g. nervous, anxious, stressed, sad, happy, neutral, burnout",
  "conversation_stage": 1, 2, 3, 4, or 5
}

Conversation Stages:
1: Identify emotion (e.g. user just stated "I'm nervous" or "I feel sad" and we don't know why)
2: Ask follow-up questions (e.g. we know the emotion and we are asking questions to explore the cause, e.g. "What is making you nervous?")
3: Understand root cause (e.g. the user replied "The students" or "My exams" and we are now exploring/validating the root cause details)
4: Provide recommendations (e.g. the root cause is understood, we are now providing coping exercises/guidance/CBT support)
5: Create action plan (e.g. we are outlining a concrete step-by-step plan or daily wellness goals)

Transition Heuristics:
- If the user's message is short and just answering a follow-up question (e.g. "the students" in response to "what is making you nervous?"), we are in Stage 3 (Understand root cause) and exploring the topic.
- Do not jump to Stage 4 or 5 unless the root cause is fully explained or detailed by the user. Keep it in Stage 2 or 3 to maintain depth.
- If the user message is detailed and root cause is already clear, transition to Stage 4.

Do not output any text other than the JSON object. Do not include markdown code block formatting. Respond with just raw JSON.
"""

def update_conversation_state(conversation_id, user_message, recent_history_str):
    prev_state = db.get_conversation_state(conversation_id)
    prev_topic = prev_state['current_topic'] if prev_state else "general"
    prev_emotion = prev_state['current_emotion'] if prev_state else "neutral"
    prev_stage = prev_state['conversation_stage'] if prev_state else 1
    
    user_prompt = f"""
Previous State:
- Topic: {prev_topic}
- Emotion: {prev_emotion}
- Stage: {prev_stage}

Recent Conversation History:
{recent_history_str}

Latest User Message: "{user_message}"
"""
    try:
        response = call_gemini(STATE_TRACKER_PROMPT, user_prompt, temperature=0.1, json_mode=True)
        state_data = json.loads(response)
        
        current_topic = state_data.get("current_topic", prev_topic)
        current_emotion = state_data.get("current_emotion", prev_emotion)
        conversation_stage = state_data.get("conversation_stage", prev_stage)
        
        # Save to database
        db.save_conversation_state(conversation_id, current_topic, current_emotion, conversation_stage)
        return {
            "current_topic": current_topic,
            "current_emotion": current_emotion,
            "conversation_stage": conversation_stage
        }
    except Exception as e:
        print(f"Error in state tracking: {e}")
        # Default state fallback
        return {
            "current_topic": prev_topic,
            "current_emotion": prev_emotion,
            "conversation_stage": prev_stage
        }

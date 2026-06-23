import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def get_chat_response(history, api_key=None):
    conversation = ""

    for msg in history[-10:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        conversation += f"{role}: {content}\n"

    prompt = f"""
You are CalmMind AI, a mental wellness assistant.

Analyze the user's emotional state and return ONLY valid JSON.

Required JSON format:

{{
    "response": "empathetic response",
    "mood": "😊 Positive",
    "stress_level": "Low",
    "confidence_score": 90,
    "recommendations": [
        "Take a short walk",
        "Practice breathing"
    ],
    "affirmation": "I am capable and resilient."
}}

Conversation:
{conversation}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are CalmMind AI."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        content = completion.choices[0].message.content

        try:
            return json.loads(content)
        except Exception:
            return {
                "response": content,
                "mood": "💭 Reflective",
                "stress_level": "Medium",
                "confidence_score": 85,
                "recommendations": [
                    "Take a few deep breaths",
                    "Practice self-care"
                ],
                "affirmation": "You are stronger than you think."
            }

    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "mood": "💭 Reflective",
            "stress_level": "Medium",
            "confidence_score": 50,
            "recommendations": [],
            "affirmation": ""
        }


def generate_wellness_plan(user_data, api_key=None):
    prompt = f"""
Create a wellness plan for:

Name: {user_data.get('name', '')}
Occupation: {user_data.get('occupation', '')}
Stress Level: {user_data.get('stress_level', '')}
Sleep Hours: {user_data.get('sleep_hours', '')}
Goal: {user_data.get('goal', '')}
Challenge: {user_data.get('challenge', '')}

Return ONLY JSON:

{{
    "morning_routine": [],
    "afternoon_routine": [],
    "evening_routine": [],
    "breathing_exercise": {{
        "name": "",
        "instructions": "",
        "duration": "",
        "benefits": ""
    }},
    "affirmation": "",
    "weekly_guidance": []
}}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        content = completion.choices[0].message.content

        try:
            return json.loads(content)
        except Exception:
            return {
                "morning_routine": [
                    "Drink water",
                    "Stretch"
                ],
                "afternoon_routine": [
                    "Walk 10 minutes"
                ],
                "evening_routine": [
                    "Journal thoughts"
                ],
                "breathing_exercise": {
                    "name": "Box Breathing",
                    "instructions": "4-4-4-4 cycle",
                    "duration": "5 minutes",
                    "benefits": "Reduces stress"
                },
                "affirmation": "I am calm and capable.",
                "weekly_guidance": [
                    "Take breaks",
                    "Sleep consistently"
                ]
            }

    except Exception:
        return {
            "morning_routine": [],
            "afternoon_routine": [],
            "evening_routine": [],
            "breathing_exercise": {},
            "affirmation": "",
            "weekly_guidance": []
        }
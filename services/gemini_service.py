import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = None

def get_groq_client():
    global client
    if client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            client = Groq(api_key=api_key)
    return client

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

    cli = get_groq_client()
    if not cli:
        return {
            "response": "Error: Groq API key is not configured. Please add GROQ_API_KEY to your env/Render settings.",
            "mood": "💭 Reflective",
            "stress_level": "Medium",
            "confidence_score": 50,
            "recommendations": [],
            "affirmation": ""
        }

    try:
        completion = cli.chat.completions.create(
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

    cli = get_groq_client()
    if not cli:
        raise ValueError("Groq client not configured")

    try:
        completion = cli.chat.completions.create(
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

def call_gemini(system_prompt, user_prompt, temperature=0.7, json_mode=False, max_tokens=None):
    """
    Invokes the Groq Llama 3 model with a system prompt and a user prompt.
    Keeps the function name for backward compatibility with existing agent files.
    """
    global api_key
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return "Error: Groq API key is not configured. Please add GROQ_API_KEY to your .env file."
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Use Llama 3.1 8B as primary for speed, and Llama 3 8B as fallback
    model_name = "llama-3.1-8b-instant"
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    
    if max_tokens:
        payload["max_tokens"] = max_tokens
        
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
        
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        # Fallback to Llama 3 8B model
        try:
            payload["model"] = "llama3-8b-8192"
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e2:
            return f"Error communicating with Groq API: {str(e2)}"
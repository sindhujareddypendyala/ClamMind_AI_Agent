import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Groq API Key
api_key = os.getenv("GROQ_API_KEY")

def get_gemini_client():
    """Returns true if Groq API key is configured, otherwise false."""
    return api_key is not None

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

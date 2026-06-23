from services.gemini_service import call_gemini
from prompts.templates import DOMAIN_GUARD_PROMPT

BLOCK_RESPONSE = """I am here as your mental wellness companion to support you with stress, anxiety, mindfulness, and emotional well-being. 

I cannot help with coding, politics, sports, movies, or general knowledge topics. 

Please feel free to share how you are feeling or let me know if you want to try a breathing exercise! 💚"""

def check_domain(user_message):
    """
    Returns (is_allowed, response_text).
    If is_allowed is False, the response_text is the polite refusal.
    """
    # Quick keyword filter to save API call costs for obvious non-wellness items
    lower_msg = user_message.lower().strip()
    non_wellness_keywords = [
        "write a python", "write a code", "write a script", "c++", "java code", "dsa problem",
        "solve this equation", "who is the prime minister", "who won the match", "cricket score",
        "movie review", "how to build a website"
    ]
    for kw in non_wellness_keywords:
        if kw in lower_msg:
            return False, BLOCK_RESPONSE

    # Call Gemini to verify
    response = call_gemini(DOMAIN_GUARD_PROMPT, f"User Message: {user_message}", temperature=0.0, max_tokens=10)
    decision = response.strip().upper()
    
    if "BLOCK" in decision:
        return False, BLOCK_RESPONSE
    return True, ""

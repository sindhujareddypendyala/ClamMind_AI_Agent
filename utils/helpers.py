# Utility Helper Functions for CalmMind AI
import re

def clean_text_for_tts(text):
    """
    Cleans markdown styling and emoji symbols from responses so that
    Text-to-Speech output sounds clean and natural.
    """
    if not text:
        return ""
        
    # Remove emojis
    clean = text.replace("💚", "").replace("🌱", "").replace("🧘", "").replace("🔮", "").replace("❓", "")
    
    # Remove markdown headers and asterisks
    clean = clean.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
    
    # Remove brackets
    clean = re.sub(r'\[.*?\]', '', clean)
    
    # Clean up whitespace
    clean = " ".join(clean.split())
    
    return clean

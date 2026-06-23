import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend directory is in the Python path for relative imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import init_db
from routers import auth, chat, mood, plans, favorites, voice

app = FastAPI(title="CalmMind AI API", version="1.0.0")

# Enable CORS for React frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify the React dev server url (e.g. http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema
init_db()

# Register API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication & Settings"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat Companion"])
app.include_router(mood.router, prefix="/api/mood", tags=["Mood Tracker"])
app.include_router(plans.router, prefix="/api/plans", tags=["Wellness Planner"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice Input & TTS"])

@app.get("/")
def read_root():
    return {"message": "CalmMind AI API is active. Exposing endpoints for React application."}

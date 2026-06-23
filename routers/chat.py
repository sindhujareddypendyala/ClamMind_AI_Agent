from fastapi import APIRouter, HTTPException, Query, Header, Depends
from pydantic import BaseModel
from typing import Optional, List
import database.db_manager as db
from services.agent_pipeline import run_agent_pipeline

router = APIRouter()

class ConversationCreateSchema(BaseModel):
    title: Optional[str] = None

class ConversationRenameSchema(BaseModel):
    title: str

class MessageCreateSchema(BaseModel):
    conversation_id: int
    message: str

def get_current_user_id(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing. Please onboard first.")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id value.")

@router.get("/conversations")
def get_conversations(user_id: int = Depends(get_current_user_id)):
    return db.get_conversations(user_id)

@router.post("/conversations")
def create_conversation(data: ConversationCreateSchema, user_id: int = Depends(get_current_user_id)):
    from datetime import datetime
    title = data.title
    if not title:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"Session - {now_str}"
        
    conv_id = db.create_conversation(user_id, title)
    conv = db.get_conversation(conv_id)
    return {"status": "success", "conversation": conv}

@router.delete("/conversations/{id}")
def delete_conversation(id: int, user_id: int = Depends(get_current_user_id)):
    conv = db.get_conversation(id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this conversation.")
        
    db.delete_conversation(id)
    return {"status": "success", "message": "Conversation deleted successfully."}

@router.post("/conversations/{id}/rename")
def rename_conversation(id: int, data: ConversationRenameSchema, user_id: int = Depends(get_current_user_id)):
    conv = db.get_conversation(id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to rename this conversation.")
        
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    db.rename_conversation(id, data.title.strip())
    return {"status": "success", "message": "Conversation renamed successfully."}

@router.post("/conversations/{id}/pin")
def pin_conversation(id: int, user_id: int = Depends(get_current_user_id)):
    conv = db.get_conversation(id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to pin this conversation.")
        
    conn = db.get_db_connection()
    row = conn.execute("SELECT * FROM conversations WHERE id = ?", (id,)).fetchone()
    current_pin = 0
    try:
        current_pin = row['pinned']
    except IndexError:
        conn.execute("ALTER TABLE conversations ADD COLUMN pinned INTEGER DEFAULT 0")
        conn.commit()
        row = conn.execute("SELECT * FROM conversations WHERE id = ?", (id,)).fetchone()
        current_pin = row['pinned']
        
    new_pin = 1 if current_pin == 0 else 0
    conn.execute("UPDATE conversations SET pinned = ? WHERE id = ?", (new_pin, id))
    conn.commit()
    conn.close()
    
    state = "pinned" if new_pin == 1 else "unpinned"
    return {"status": "success", "message": f"Conversation {state} successfully.", "pinned": new_pin == 1}

@router.get("/messages")
def get_messages(conversation_id: int = Query(..., alias="conversation_id"), user_id: int = Depends(get_current_user_id)):
    conv = db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation.")
        
    return db.get_conversation_messages(conversation_id)

@router.post("/message")
def send_message(data: MessageCreateSchema, user_id: int = Depends(get_current_user_id)):
    conv = db.get_conversation(data.conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to message in this conversation.")
        
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    db.add_message(data.conversation_id, "user", data.message.strip())
    pipeline_res = run_agent_pipeline(user_id, data.conversation_id, data.message.strip())
    db.add_message(data.conversation_id, "assistant", pipeline_res["content"])
    
    # Auto-log detected emotion and mapped wellness score
    detected_emotion = pipeline_res.get("emotion", "neutral").lower()
    
    # Normalize to specified emotion categories
    norm_emotion = "neutral"
    if detected_emotion in ["happy", "calm", "positive"]:
        norm_emotion = "positive"
    elif detected_emotion in ["stressed", "overwhelmed", "stress"]:
        norm_emotion = "stress"
    elif detected_emotion in ["anxious", "overthinking", "anxiety", "angry"]:
        norm_emotion = "anxiety"
    elif detected_emotion in ["sad", "lonely", "sadness"]:
        norm_emotion = "sadness"
    elif detected_emotion in ["burnout", "tired"]:
        norm_emotion = "burnout"
    else:
        norm_emotion = "neutral"

    score_mapping = {
        "positive": 100,
        "neutral": 70,
        "stress": 50,
        "anxiety": 40,
        "sadness": 40,
        "burnout": 30
    }
    wellness_score = score_mapping.get(norm_emotion, 70)
    db.log_auto_mood(user_id, data.conversation_id, norm_emotion, wellness_score)
    
    return {
        "status": "success",
        "response": pipeline_res
    }

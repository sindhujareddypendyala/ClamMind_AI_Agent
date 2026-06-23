from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import database.db_manager as db

router = APIRouter()

class FavoriteCreateSchema(BaseModel):
    type: str  # e.g., "response", "exercise", "plan"
    content: str

@router.get("")
def get_favorites(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        return []
    try:
        user_id = int(x_user_id)
    except ValueError:
        return []
    return db.get_favorites(user_id)

@router.post("")
def add_favorite(data: FavoriteCreateSchema, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")
        
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty.")
        
    fav_id = db.add_favorite(user_id, data.type.strip(), data.content.strip())
    return {
        "status": "success",
        "message": "Added to favorites successfully.",
        "favorite_id": fav_id
    }

@router.delete("/{id}")
def delete_favorite(id: int, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")
        
    # Verify ownership
    conn = db.get_db_connection()
    fav = conn.execute("SELECT * FROM favorites WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite item not found.")
    if fav['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this favorite.")
        
    db.delete_favorite(id)
    return {"status": "success", "message": "Favorite item removed successfully."}

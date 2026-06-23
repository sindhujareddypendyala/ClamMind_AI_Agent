from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import database.db_manager as db

router = APIRouter()

class ProfileSchema(BaseModel):
    name: str
    age: int
    occupation: str

@router.get("/profile")
def get_profile(x_user_id: Optional[str] = Header(None)):
    user = None
    if x_user_id:
        try:
            user = db.get_user_by_id(int(x_user_id))
        except:
            pass
            
    if not user:
        return {"logged_in": False, "user": None}
    return {"logged_in": True, "user": user}

@router.post("/profile")
def save_profile(profile: ProfileSchema, x_user_id: Optional[str] = Header(None)):
    if not profile.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty.")
    
    user = None
    if x_user_id:
        try:
            user = db.get_user_by_id(int(x_user_id))
        except:
            pass
            
    if user:
        db.update_user(user['id'], profile.name.strip(), profile.age, profile.occupation.strip())
        user_id = user['id']
    else:
        user_id = db.create_user(profile.name.strip(), profile.age, profile.occupation.strip())
    
    updated_user = db.get_user_by_id(user_id)
    return {"status": "success", "message": "Profile saved successfully.", "user": updated_user}

@router.delete("/profile/{user_id}")
def delete_profile(user_id: int, x_user_id: Optional[str] = Header(None)):
    if x_user_id and int(x_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this profile.")
        
    existing_user = db.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User profile not found.")
    db.delete_user_profile(user_id)
    return {"status": "success", "message": "Profile and all associated data deleted."}

@router.get("/export/{user_id}")
def export_data(user_id: int, x_user_id: Optional[str] = Header(None)):
    if x_user_id and int(x_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data.")
        
    existing_user = db.get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User profile not found.")
    data = db.export_user_data(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data available to export.")
    return data

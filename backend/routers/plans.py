from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
import database.db_manager as db
import json
from agents.wellness_planner_agent import generate_personalized_plan, DESCRIPTIONS

router = APIRouter()

class PlanCreateSchema(BaseModel):
    plan_type: str  # e.g., "Stress Recovery Plan"

class TaskSchema(BaseModel):
    task: str
    done: bool

class PlanUpdateSchema(BaseModel):
    tasks: List[TaskSchema]

@router.get("")
def get_plans(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        return []
    try:
        user_id = int(x_user_id)
    except ValueError:
        return []
        
    plans = db.get_wellness_plans(user_id)
    for plan in plans:
        if isinstance(plan.get('tasks_json'), str):
            try:
                plan['tasks'] = json.loads(plan['tasks_json'])
            except:
                plan['tasks'] = []
        else:
            plan['tasks'] = plan.get('tasks_json') or []
    return plans

@router.post("")
def generate_plan(data: PlanCreateSchema, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")
        
    plan_id = generate_personalized_plan(user_id, data.plan_type)
    return {
        "status": "success",
        "message": f"Generated and saved '{data.plan_type}' successfully.",
        "plan_id": plan_id
    }

@router.put("/{id}")
def update_plan(id: int, data: PlanUpdateSchema, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")

    # Retrieve existing plan to check ownership
    conn = db.get_db_connection()
    plan = conn.execute("SELECT * FROM wellness_plans WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Wellness plan not found.")
    if plan['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this plan.")
        
    tasks_list = [t.model_dump() for t in data.tasks]
    total_tasks = len(tasks_list)
    
    if total_tasks == 0:
        progress = 0.0
        completed = 0
    else:
        done_count = sum(1 for t in tasks_list if t['done'])
        progress = (done_count / total_tasks) * 100.0
        completed = 1 if done_count == total_tasks else 0
        
    db.update_wellness_plan(id, tasks_list, progress, completed)
    return {
        "status": "success",
        "message": "Wellness plan updated successfully.",
        "progress": progress,
        "completed": completed == 1
    }

@router.delete("/{id}")
def delete_plan(id: int, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")

    # Check ownership
    conn = db.get_db_connection()
    plan = conn.execute("SELECT * FROM wellness_plans WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Wellness plan not found.")
    if plan['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this plan.")
        
    db.delete_wellness_plan(id)
    return {"status": "success", "message": "Wellness plan deleted successfully."}

class PersonalizedPlanRequestSchema(BaseModel):
    goal: str
    stress_level: int
    sleep_quality: int
    available_time: str
    activities: List[str]
    challenge: str

@router.post("/generate_personalized")
def generate_personalized_plan_endpoint(data: PersonalizedPlanRequestSchema, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")

    # Fetch mood logs for context
    logs = db.get_mood_logs(user_id, days=7)
    recent_moods = [f"Mood: {l['mood']} (Stress: {l['stress_level']}, Sleep: {l['sleep_hours']}h)" for l in logs]
    mood_context = "\n".join(recent_moods) if recent_moods else "No logs recorded yet."

    system_prompt = """You are the AI Personal Wellness Planner for CalmMind AI.
Your task is to generate a highly personalized wellness plan for a user based on their specific inputs, mood history, and primary challenges.

You must respond with a JSON object containing the plan structure.
The JSON object must have exactly these keys:
{
  "title": "A customized title for the plan",
  "description": "A warm, empathetic 2-sentence summary of what this plan will achieve",
  "tasks": [
    {"task": "Morning: [A micro-task taking less than daily available time, incorporating preferred activities]", "done": false},
    {"task": "Afternoon: [A micro-task suitable for daytime]", "done": false},
    {"task": "Evening: [A relaxing task to wind down]", "done": false},
    {"task": "Weekly Goal: [A specific, measurable outcome (e.g. reduce stress score from X to Y)]", "done": false}
  ]
}

Ensure the tasks are concrete, helpful, and respect the user's daily available time limit and preferred activities.
Do not output any text other than the JSON object. Do not include markdown code block formatting. Respond with just raw JSON.
"""

    user_prompt = f"""
User Goal: {data.goal}
Current Stress Level: {data.stress_level}/10
Current Sleep Quality: {data.sleep_quality}/10
Daily Available Time: {data.available_time}
Preferred Activities: {", ".join(data.activities)}
Primary Challenge: {data.challenge}

Recent Mood Logs Context:
{mood_context}
"""

    try:
        from services.gemini_service import call_gemini
        llm_response = call_gemini(system_prompt, user_prompt, temperature=0.7, json_mode=True)
        plan_data = json.loads(llm_response)
        
        # Save in database
        plan_id = db.create_wellness_plan(
            user_id=user_id,
            plan_type=data.goal.split()[0], # Short category
            title=plan_data.get("title", f"Personalized {data.goal}"),
            description=plan_data.get("description", "A custom tailored plan."),
            tasks=plan_data.get("tasks", [])
        )
        
        return {
            "status": "success",
            "message": "Personalized plan generated successfully.",
            "plan_id": plan_id
        }
    except Exception as e:
        print(f"Error generating personalized plan: {e}")
        # Fallback to standard planner agent if Groq call fails
        from agents.wellness_planner_agent import generate_personalized_plan
        plan_id = generate_personalized_plan(user_id, f"{data.goal} Plan")
        return {
            "status": "success",
            "message": "Generated standard plan as fallback.",
            "plan_id": plan_id
        }

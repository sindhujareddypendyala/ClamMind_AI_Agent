from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional, List
import database.db_manager as db
from agents.mood_prediction_agent import analyze_mood_trends

router = APIRouter()

class MoodLogSchema(BaseModel):
    mood: str
    stress_level: int
    anxiety_level: int
    energy_level: int
    sleep_hours: float
    trigger: Optional[str] = ""
    notes: Optional[str] = ""

@router.post("/log")
def log_mood(data: MoodLogSchema, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")
        
    log_id = db.log_mood(
        user_id=user_id,
        mood=data.mood,
        stress_level=data.stress_level,
        anxiety_level=data.anxiety_level,
        energy_level=data.energy_level,
        sleep_hours=data.sleep_hours,
        trigger=data.trigger,
        notes=data.notes
    )
    
    return {
        "status": "success",
        "message": "Mood logged successfully.",
        "log_id": log_id
    }

@router.get("/logs")
def get_mood_logs(days: int = 30, x_user_id: Optional[str] = Header(None)):
    import datetime
    if not x_user_id:
        return {"logs": [], "analytics": {}}
    try:
        user_id = int(x_user_id)
    except ValueError:
        return {"logs": [], "analytics": {}}
        
    # Fetch a larger history (up to 100 entries) to compute daily/weekly/monthly trends accurately
    all_logs = db.get_mood_logs(user_id, days=100)
    
    # Slice to the requested range for the display logs
    display_logs = all_logs[-days:] if len(all_logs) > days else all_logs
    
    if not all_logs:
        analytics = {
            "average_stress": 0,
            "average_anxiety": 0,
            "average_energy": 0,
            "average_sleep": 0,
            "mood_counts": {},
            "wellness_score": 0,
            "wellness_trend": "Stable",
            "emotion_distribution": {
                "stress": 0, "anxiety": 0, "sadness": 0, "positive": 0, "neutral": 0, "burnout": 0
            },
            "daily_trends": [],
            "weekly_trends": [],
            "monthly_trends": [],
            "insights": ["Start logging your mood to see insights!"],
            "recommendations": [{"icon": "🧘", "text": "Mindfulness Meditation", "type": "meditation"}]
        }
    else:
        # 1. Standard Averages (calculated on the requested 'days' slice)
        total_stress = sum(l['stress_level'] for l in display_logs)
        total_anxiety = sum(l['anxiety_level'] for l in display_logs)
        total_energy = sum(l['energy_level'] for l in display_logs)
        total_sleep = sum(l['sleep_hours'] for l in display_logs)
        count = len(display_logs)
        
        mood_counts = {}
        for l in display_logs:
            m = l['mood']
            if m:
                mood_counts[m] = mood_counts.get(m, 0) + 1
            
        avg_stress = total_stress / count if count > 0 else 0
        avg_anxiety = total_anxiety / count if count > 0 else 0
        avg_energy = total_energy / count if count > 0 else 0
        avg_sleep = total_sleep / count if count > 0 else 0
        
        # 2. Overall Wellness Score (calculated from recent auto or manual logs)
        recent_scores = []
        for l in reversed(all_logs): # latest first
            score = l.get('wellness_score')
            if score is not None and score > 0:
                recent_scores.append(score)
            else:
                # manual fallback
                ml_stress = l['stress_level']
                ml_anxiety = l['anxiety_level']
                ml_energy = l['energy_level']
                ml_sleep = l['sleep_hours']
                ml_sleep_score = min(ml_sleep * 1.25, 10.0)
                ml_score = int(((ml_energy + (10 - ml_stress) + (10 - ml_anxiety) + ml_sleep_score) / 4.0) * 10.0)
                recent_scores.append(max(0, min(100, ml_score)))
            if len(recent_scores) >= 7:
                break
        
        wellness_score = int(sum(recent_scores) / len(recent_scores)) if recent_scores else 70
        
        # 3. Wellness Trend
        # Compare current week (last 7 scores) and previous week (previous 7 scores)
        all_period_scores = []
        for l in all_logs:
            score = l.get('wellness_score')
            if score is not None and score > 0:
                all_period_scores.append(score)
            else:
                ml_stress = l['stress_level']
                ml_anxiety = l['anxiety_level']
                ml_energy = l['energy_level']
                ml_sleep = l['sleep_hours']
                ml_sleep_score = min(ml_sleep * 1.25, 10.0)
                ml_score = int(((ml_energy + (10 - ml_stress) + (10 - ml_anxiety) + ml_sleep_score) / 4.0) * 10.0)
                all_period_scores.append(max(0, min(100, ml_score)))
        
        if len(all_period_scores) >= 2:
            recent_avg = sum(all_period_scores[-7:]) / len(all_period_scores[-7:])
            prev_avg_scores = all_period_scores[-14:-7]
            if prev_avg_scores:
                prev_avg = sum(prev_avg_scores) / len(prev_avg_scores)
                if recent_avg > prev_avg + 5:
                    wellness_trend = "Improving"
                elif recent_avg < prev_avg - 5:
                    wellness_trend = "Declining"
                else:
                    wellness_trend = "Stable"
            else:
                wellness_trend = "Stable"
        else:
            wellness_trend = "Stable"

        # 4. Emotion Distribution (percentage)
        emotion_counts = {
            "stress": 0, "anxiety": 0, "sadness": 0, "positive": 0, "neutral": 0, "burnout": 0
        }
        total_emotions = 0
        
        for l in all_logs:
            em = l.get('emotion')
            if em:
                em = em.lower()
                # Map standard variants
                if em in ["happy", "calm", "positive"]:
                    em = "positive"
                elif em in ["stressed", "overwhelmed", "stress"]:
                    em = "stress"
                elif em in ["anxious", "overthinking", "anxiety", "angry"]:
                    em = "anxiety"
                elif em in ["sad", "lonely", "sadness"]:
                    em = "sadness"
                elif em in ["burnout", "tired"]:
                    em = "burnout"
                
                if em in emotion_counts:
                    emotion_counts[em] += 1
                    total_emotions += 1
        
        # Fallback to mapping manual logs if no auto logs are present
        if total_emotions == 0:
            for l in all_logs:
                m = (l.get('mood') or '').lower()
                if m in ["happy", "calm", "positive"]:
                    em = "positive"
                elif m in ["stressed", "stress", "overwhelmed"]:
                    em = "stress"
                elif m in ["anxious", "anxiety", "angry"]:
                    em = "anxiety"
                elif m in ["sad", "sadness", "lonely"]:
                    em = "sadness"
                elif m in ["burnout", "tired"]:
                    em = "burnout"
                else:
                    em = "neutral"
                
                emotion_counts[em] += 1
                total_emotions += 1
                
        emotion_distribution = {}
        for k, v in emotion_counts.items():
            emotion_distribution[k] = int((v / total_emotions) * 100) if total_emotions > 0 else 0
            
        # 5. Trends Charts Aggregates
        # Helper to parse dates
        def parse_date(date_str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
                try:
                    return datetime.datetime.strptime(date_str.split(".")[0].replace("T", " "), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
            try:
                return datetime.datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d")
            except ValueError:
                return datetime.datetime.now()

        # Daily trends
        by_date = {}
        for idx, l in enumerate(all_logs):
            dt = parse_date(l['created_at'])
            date_str = dt.strftime("%b %d")
            by_date.setdefault(date_str, []).append(all_period_scores[idx])
        daily_trends = [{"date": k, "score": int(sum(v)/len(v))} for k, v in by_date.items()][-10:]
        
        # Weekly trends
        by_week = {}
        for idx, l in enumerate(all_logs):
            dt = parse_date(l['created_at'])
            week_str = f"Wk {dt.isocalendar()[1]}"
            by_week.setdefault(week_str, []).append(all_period_scores[idx])
        weekly_trends = [{"week": k, "score": int(sum(v)/len(v))} for k, v in by_week.items()][-6:]
        
        # Monthly trends
        by_month = {}
        for idx, l in enumerate(all_logs):
            dt = parse_date(l['created_at'])
            month_str = dt.strftime("%b")
            by_month.setdefault(month_str, []).append(all_period_scores[idx])
        monthly_trends = [{"month": k, "score": int(sum(v)/len(v))} for k, v in by_month.items()][-6:]

        # 6. Insights
        insights = []
        
        # Stress Insight
        stress_count_recent = sum(1 for l in all_logs[-7:] if l.get('emotion') == 'stress' or (l.get('mood') or '').lower() in ['stressed', 'stress'])
        if stress_count_recent >= 2:
            insights.append("You have reported stress frequently during the last 7 days.")
            
        # Mood Change Insight
        if wellness_trend == "Improving":
            insights.append("Your mood has improved compared to last week.")
        elif wellness_trend == "Declining":
            insights.append("Your mood has declined compared to last week.")
            
        # Sleep Insight
        low_sleep_count = sum(1 for l in all_logs[-7:] if l.get('sleep_hours') and l.get('sleep_hours') < 6.0)
        
        # Count conversation sleep mentions
        conn = db.get_db_connection()
        sleep_convs = conn.execute("""
            SELECT COUNT(DISTINCT conversation_id) as count 
            FROM messages 
            WHERE content LIKE '%sleep%' OR content LIKE '%insomnia%' OR content LIKE '%tired%' OR content LIKE '%wake up%'
        """).fetchone()
        sleep_count = sleep_convs['count'] if sleep_convs else 0
        conn.close()
        
        if sleep_count > 0:
            insights.append(f"Sleep-related concerns appeared in {sleep_count} conversations.")
        elif low_sleep_count >= 2:
            insights.append(f"Sleep duration has been below 6 hours in {low_sleep_count} of your recent check-ins.")
            
        if not insights:
            insights.append("Your emotional pattern is stable. Continue logging your mood daily!")
            
        # 7. Recommendations
        recommendations = []
        if stress_count_recent >= 2:
            recommendations.append({
                "icon": "🌬",
                "text": "Breathing Exercise",
                "type": "breathing"
            })
            
        burnout_count = sum(1 for l in all_logs[-7:] if l.get('emotion') == 'burnout' or (l.get('mood') or '').lower() in ['burnout', 'tired'])
        if burnout_count >= 2 or wellness_score < 45:
            recommendations.append({
                "icon": "📋",
                "text": "Recovery Plan",
                "type": "plan"
            })
            
        if sleep_count >= 2 or low_sleep_count >= 2:
            recommendations.append({
                "icon": "😴",
                "text": "Sleep Improvement Program",
                "type": "sleep"
            })
            
        if not recommendations:
            recommendations.append({
                "icon": "🧘",
                "text": "Mindfulness Meditation",
                "type": "meditation"
            })
            recommendations.append({
                "icon": "📓",
                "text": "Gratitude Journaling",
                "type": "journaling"
            })

        analytics = {
            "average_stress": round(avg_stress, 1),
            "average_anxiety": round(avg_anxiety, 1),
            "average_energy": round(avg_energy, 1),
            "average_sleep": round(avg_sleep, 1),
            "mood_counts": mood_counts,
            "wellness_score": wellness_score,
            "wellness_trend": wellness_trend,
            "emotion_distribution": emotion_distribution,
            "daily_trends": daily_trends,
            "weekly_trends": weekly_trends,
            "monthly_trends": monthly_trends,
            "insights": insights,
            "recommendations": recommendations
        }
        
    return {
        "logs": logs,
        "analytics": analytics
    }

@router.get("/predict")
def predict_mood(days: int = 30, x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id.")
    
    result = analyze_mood_trends(user_id, days=days)
    return result

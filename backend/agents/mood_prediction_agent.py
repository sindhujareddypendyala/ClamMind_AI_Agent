import database.db_manager as db
from services.gemini_service import call_gemini
from prompts.templates import MOOD_PREDICTION_PROMPT
import pandas as pd
import numpy as np

def get_mood_pipeline_context(user_id):
    """
    Retrieves a simple text summary of mood logs to feed into the chat agent pipeline.
    """
    logs = db.get_mood_logs(user_id, days=14)
    if not logs:
        return "Mood History: User has not logged any mood entries yet."
    
    # Calculate simple stats
    df = pd.DataFrame(logs)
    avg_stress = df['stress_level'].mean()
    avg_anxiety = df['anxiety_level'].mean()
    common_mood = df['mood'].mode()[0] if not df['mood'].empty else "neutral"
    
    context_summary = (
        f"Mood History: In the last 14 days, the user logged mood {len(logs)} times. "
        f"Most frequent mood: {common_mood}. Average Stress: {avg_stress:.1f}/10. "
        f"Average Anxiety: {avg_anxiety:.1f}/10."
    )
    return context_summary

def analyze_mood_trends(user_id, days=14):
    """
    Performs detailed trend prediction and analysis for the Mood Prediction page.
    Returns a dictionary with trend summaries and recommendations.
    """
    logs = db.get_mood_logs(user_id, days=days)
    if not logs:
        return {
            "success": False,
            "message": "No mood logs found for the selected time range. Please log your mood first under 'Mood Tracker'."
        }
    
    # Process with pandas
    df = pd.DataFrame(logs)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Calculate stats
    avg_stress = df['stress_level'].mean()
    avg_anxiety = df['anxiety_level'].mean()
    avg_energy = df['energy_level'].mean()
    avg_sleep = df['sleep_hours'].mean()
    
    # Determine slope of stress and anxiety trends (simple linear regression slope or diff)
    stress_trend_label = "Stable"
    anxiety_trend_label = "Stable"
    
    if len(df) > 1:
        stress_diff = df['stress_level'].iloc[-1] - df['stress_level'].iloc[0]
        anxiety_diff = df['anxiety_level'].iloc[-1] - df['anxiety_level'].iloc[0]
        
        if stress_diff > 1.5:
            stress_trend_label = "Increasing (Stress is rising)"
        elif stress_diff < -1.5:
            stress_trend_label = "Decreasing (Stress is resolving)"
            
        if anxiety_diff > 1.5:
            anxiety_trend_label = "Increasing (Anxiety is rising)"
        elif anxiety_diff < -1.5:
            anxiety_trend_label = "Decreasing (Anxiety is resolving)"

    # Format log text data for Gemini
    logs_summary = ""
    for _, row in df.iterrows():
        date_str = row['created_at'].strftime('%Y-%m-%d')
        logs_summary += f"Date: {date_str} | Mood: {row['mood']} | Stress: {row['stress_level']}/10 | Anxiety: {row['anxiety_level']}/10 | Energy: {row['energy_level']}/10 | Sleep: {row['sleep_hours']}h | Trigger: {row['trigger']} | Notes: {row['notes']}\n"
    
    user_prompt = f"""Timeframe: Last {days} Days
Logs Count: {len(df)}
Averages:
- Stress: {avg_stress:.1f}/10
- Anxiety: {avg_anxiety:.1f}/10
- Energy: {avg_energy:.1f}/10
- Sleep: {avg_sleep:.2f} hours/night

Detailed Logs:
{logs_summary}

Please analyze these logs and generate a structured summary. Make sure to estimate their current coping 'Confidence %' based on high energy, low stress, and good sleep, and offer wellness prediction & recommendations.
"""
    try:
        analysis_text = call_gemini(MOOD_PREDICTION_PROMPT, user_prompt, temperature=0.5)
    except Exception as e:
        analysis_text = f"Unable to generate detailed insights via Gemini. Current averages: Stress: {avg_stress:.1f}, Anxiety: {avg_anxiety:.1f}, Sleep: {avg_sleep:.1f}h."

    return {
        "success": True,
        "logs_count": len(df),
        "avg_stress": round(avg_stress, 1),
        "avg_anxiety": round(avg_anxiety, 1),
        "avg_energy": round(avg_energy, 1),
        "avg_sleep": round(avg_sleep, 1),
        "stress_trend": stress_trend_label,
        "anxiety_trend": anxiety_trend_label,
        "analysis": analysis_text
    }

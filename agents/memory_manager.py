import database.db_manager as db

def get_context_memory(user_id, conversation_id=None, num_messages=5):
    """
    Retrieves and structures the user's profile, recent messages, mood logs, 
    wellness plans, and triggers to inject memory into the agent pipeline.
    """
    # 1. User profile
    user = db.get_user()
    if not user:
        return "User Profile: Not created yet."

    user_info = f"User Profile:\n- Name: {user['name']}\n- Age: {user['age']}\n- Occupation: {user['occupation']}\n"

    # 2. Recent Messages
    history_str = "Recent Conversation History:\n"
    if conversation_id:
        messages = db.get_conversation_messages(conversation_id)
        # Get last N messages
        recent_messages = messages[-num_messages:] if len(messages) > num_messages else messages
        if recent_messages:
            for msg in recent_messages:
                role = "User" if msg['role'] == "user" else "Companion"
                history_str += f"- {role}: {msg['content']}\n"
        else:
            history_str += "- No messages yet in this conversation.\n"
    else:
        history_str += "- No active conversation selected.\n"

    # 3. Recent Mood Logs
    mood_str = "Recent Mood Logs (Last 7 Logs):\n"
    mood_logs = db.get_mood_logs(user_id, days=7)
    if mood_logs:
        triggers = []
        for log in mood_logs:
            mood_str += f"- {log['created_at'].split()[0] if ' ' in log['created_at'] else log['created_at']}: Mood={log['mood']}, Stress={log['stress_level']}/10, Anxiety={log['anxiety_level']}/10, Energy={log['energy_level']}/10, Sleep={log['sleep_hours']}h\n"
            if log['trigger']:
                triggers.append(log['trigger'])
        if triggers:
            mood_str += f"- Key Triggers Noted: {', '.join(set(triggers))}\n"
    else:
        mood_str += "- No mood logs recorded yet.\n"

    # 4. Active Wellness Plans
    plans_str = "Active Wellness Plans:\n"
    plans = db.get_wellness_plans(user_id)
    active_plans = [p for p in plans if p['completed'] == 0]
    if active_plans:
        for plan in active_plans:
            plans_str += f"- Plan: {plan['title']} ({plan['type']}) | Progress: {plan['progress']:.1f}%\n"
    else:
        plans_str += "- No active wellness plans.\n"

    # 5. Favorites
    fav_str = "Favorites (Saved Quotes & Exercises):\n"
    favs = db.get_favorites(user_id)
    if favs:
        # Show a summary of up to 3 favorites
        for fav in favs[:3]:
            fav_str += f"- [{fav['type']}]: {fav['content'][:60]}...\n"
    else:
        fav_str += "- No favorites saved yet.\n"

    # Combine everything
    full_context = f"""--- USER MEMORY CONTEXT ---
{user_info}
{history_str}
{mood_str}
{plans_str}
{fav_str}
---------------------------"""
    
    return full_context

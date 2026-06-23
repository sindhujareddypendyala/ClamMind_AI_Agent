import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "calmmind.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        occupation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Conversations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Create Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    )
    """)

    # Create Mood Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mood TEXT NOT NULL,
        stress_level INTEGER NOT NULL,
        anxiety_level INTEGER NOT NULL,
        energy_level INTEGER NOT NULL,
        sleep_hours REAL NOT NULL,
        trigger TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Create Wellness Plans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wellness_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        tasks_json TEXT NOT NULL,
        progress REAL DEFAULT 0.0,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Create Favorites Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# User Operations
def get_user():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users ORDER BY id ASC LIMIT 1").fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(name, age, occupation):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, age, occupation) VALUES (?, ?, ?)",
        (name, age, occupation)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def update_user(user_id, name, age, occupation):
    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET name = ?, age = ?, occupation = ? WHERE id = ?",
        (name, age, occupation, user_id)
    )
    conn.commit()
    conn.close()

def delete_user_profile(user_id):
    conn = get_db_connection()
    # Enable foreign key cascade delete
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Conversation Operations
def create_conversation(user_id, title):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conv_id

def get_conversations(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_conversation(conversation_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_conversation(conversation_id):
    conn = get_db_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()

def rename_conversation(conversation_id, new_title):
    conn = get_db_connection()
    conn.execute(
        "UPDATE conversations SET title = ? WHERE id = ?",
        (new_title, conversation_id)
    )
    conn.commit()
    conn.close()

def get_conversation_messages(conversation_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_message(conversation_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

# Mood Log Operations
def log_mood(user_id, mood, stress_level, anxiety_level, energy_level, sleep_hours, trigger, notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mood_logs (user_id, mood, stress_level, anxiety_level, energy_level, sleep_hours, trigger, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, mood, stress_level, anxiety_level, energy_level, sleep_hours, trigger, notes))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def get_mood_logs(user_id, days=30):
    conn = get_db_connection()
    # Filter by user and optional date range
    rows = conn.execute("""
        SELECT * FROM mood_logs 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, days)).fetchall()
    conn.close()
    # Reverse to make it chronological
    logs = [dict(row) for row in rows]
    logs.reverse()
    return logs

# Wellness Plan Operations
def create_wellness_plan(user_id, plan_type, title, description, tasks):
    conn = get_db_connection()
    cursor = conn.cursor()
    tasks_json = json.dumps(tasks)
    cursor.execute("""
        INSERT INTO wellness_plans (user_id, type, title, description, tasks_json, progress, completed)
        VALUES (?, ?, ?, ?, ?, 0.0, 0)
    """, (user_id, plan_type, title, description, tasks_json))
    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return plan_id

def get_wellness_plans(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM wellness_plans WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_wellness_plan(plan_id, tasks, progress, completed):
    conn = get_db_connection()
    tasks_json = json.dumps(tasks)
    conn.execute("""
        UPDATE wellness_plans 
        SET tasks_json = ?, progress = ?, completed = ? 
        WHERE id = ?
    """, (tasks_json, progress, completed, plan_id))
    conn.commit()
    conn.close()

def delete_wellness_plan(plan_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM wellness_plans WHERE id = ?", (plan_id,))
    conn.commit()
    conn.close()

# Favorites Operations
def add_favorite(user_id, fav_type, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO favorites (user_id, type, content) VALUES (?, ?, ?)",
        (user_id, fav_type, content)
    )
    fav_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return fav_id

def get_favorites(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM favorites WHERE user_id = ? ORDER BY saved_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_favorite(fav_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM favorites WHERE id = ?", (fav_id,))
    conn.commit()
    conn.close()

# Export Data
def export_user_data(user_id):
    conn = get_db_connection()
    
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return None
    
    data = {
        "profile": dict(user),
        "conversations": [],
        "mood_logs": [],
        "wellness_plans": [],
        "favorites": []
    }
    
    # Conversations & Messages
    convs = conn.execute("SELECT * FROM conversations WHERE user_id = ?", (user_id,)).fetchall()
    for conv in convs:
        conv_dict = dict(conv)
        msgs = conn.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC", (conv['id'],)).fetchall()
        conv_dict["messages"] = [dict(msg) for msg in msgs]
        data["conversations"].append(conv_dict)
        
    # Mood logs
    moods = conn.execute("SELECT * FROM mood_logs WHERE user_id = ? ORDER BY created_at ASC", (user_id,)).fetchall()
    data["mood_logs"] = [dict(mood) for mood in moods]
    
    # Wellness plans
    plans = conn.execute("SELECT * FROM wellness_plans WHERE user_id = ?", (user_id,)).fetchall()
    data["wellness_plans"] = [dict(plan) for plan in plans]
    
    # Favorites
    favs = conn.execute("SELECT * FROM favorites WHERE user_id = ?", (user_id,)).fetchall()
    data["favorites"] = [dict(fav) for fav in favs]
    
    conn.close()
    return data

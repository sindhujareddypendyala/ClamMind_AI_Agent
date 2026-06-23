import database.db_manager as db

DESCRIPTIONS = {
    "Stress Recovery Plan": "Designed to regulate cortisol, release physiological tension, and lower daily stress levels.",
    "Burnout Recovery Plan": "Mindfulness-centric actions ensuring resting heart rates and stress boundary limits.",
    "Sleep Improvement Plan": "Mindfulness-centric actions ensuring healthy sleep hygiene, relaxation, and resting heart rates.",
    "Confidence Building Plan": "Empowerment tasks focusing on self-affirmation, positive projection, and self-esteem booster logs.",
    "Weekly Wellness Plan": "Distraction-free guidelines facilitating micro-breaks, prioritization, and deep concentration."
}

DEFAULT_TASKS = {
    "Stress Recovery Plan": [
        {"task": "Complete a 5-minute Box Breathing exercise.", "done": False},
        {"task": "Identify and write down one primary stress trigger in your mood journal.", "done": False},
        {"task": "Take a 15-minute walk outside without checking your phone.", "done": False},
        {"task": "Spend 10 minutes practice grounding or stretching.", "done": False},
        {"task": "Do a brain dump: write all worries on a paper to let them go.", "done": False}
    ],
    "Burnout Recovery Plan": [
        {"task": "Set strict work boundaries: close work laptops by 6:00 PM.", "done": False},
        {"task": "Engage in 15 minutes of quiet time or meditation.", "done": False},
        {"task": "Declutter one space in your physical environment.", "done": False},
        {"task": "Engage in a non-screen creative hobby for 30 minutes.", "done": False},
        {"task": "Decline one non-essential responsibility or request.", "done": False}
    ],
    "Sleep Improvement Plan": [
        {"task": "Disconnect from all digital screens 1 hour before bed.", "done": False},
        {"task": "Practice 3 minutes of Calm Breathing in bed.", "done": False},
        {"task": "Listen to a 10-minute Sleep Relaxation mindfulness exercise.", "done": False},
        {"task": "Maintain a dark, quiet, and cool bedroom environment.", "done": False},
        {"task": "Refrain from heavy meals or caffeine after 6:00 PM.", "done": False}
    ],
    "Confidence Building Plan": [
        {"task": "Write down 3 things you love or appreciate about yourself.", "done": False},
        {"task": "Practice the Confidence Exercise (visualizing success).", "done": False},
        {"task": "Accomplish one small task you have been putting off.", "done": False},
        {"task": "Catch yourself in a negative self-talk moment and reframe it.", "done": False},
        {"task": "Review your list of past achievements and wins.", "done": False}
    ],
    "Weekly Wellness Plan": [
        {"task": "Complete a 15-minute mental health check-in companion session.", "done": False},
        {"task": "Log your mood at least 4 times throughout the week.", "done": False},
        {"task": "Do a 10-minute Box Breathing exercise twice this week.", "done": False},
        {"task": "Spend at least 30 minutes in nature or fresh air.", "done": False},
        {"task": "Establish one daily mindfulness routine you stick to.", "done": False}
    ]
}

def generate_personalized_plan(user_id: int, plan_type: str):
    """
    Creates a wellness plan in the database for the user with predefined clinical tasks.
    """
    if plan_type not in DEFAULT_TASKS:
        plan_type = "Stress Recovery Plan"
        
    tasks = DEFAULT_TASKS[plan_type]
    desc = DESCRIPTIONS[plan_type]
    plan_type_short = plan_type.split()[0]
    
    plan_id = db.create_wellness_plan(
        user_id=user_id,
        plan_type=plan_type_short,
        title=plan_type,
        description=desc,
        tasks=tasks
    )
    return plan_id

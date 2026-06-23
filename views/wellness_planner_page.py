import streamlit as st
import database.db_manager as db
import json

def get_default_tasks(plan_type):
    """
    Returns a predefined list of tasks for the selected wellness plan type.
    """
    if plan_type == "Stress Recovery Plan":
        return [
            {"task": "Complete a 5-minute Box Breathing exercise.", "done": False},
            {"task": "Identify and write down one primary stress trigger in your mood journal.", "done": False},
            {"task": "Take a 15-minute walk outside without checking your phone.", "done": False},
            {"task": "Spend 10 minutes practice grounding or stretching.", "done": False},
            {"task": "Do a brain dump: write all worries on a paper to let them go.", "done": False}
        ]
    elif plan_type == "Anxiety Recovery Plan":
        return [
            {"task": "Perform a 4-7-8 Breathing routine to calm the nervous system.", "done": False},
            {"task": "Identify one anxious thought and challenge its validity (CBT reframing).", "done": False},
            {"task": "Engage in the 5-4-3-2-1 Grounding Exercise.", "done": False},
            {"task": "Limit caffeine and sugar intake for the day.", "done": False},
            {"task": "Recite 3 positive self-affirmations aloud.", "done": False}
        ]
    elif plan_type == "Sleep Improvement Plan":
        return [
            {"task": "Disconnect from all digital screens 1 hour before bed.", "done": False},
            {"task": "Practice 3 minutes of Calm Breathing in bed.", "done": False},
            {"task": "Listen to a 10-minute Sleep Relaxation mindfulness exercise.", "done": False},
            {"task": "Maintain a dark, quiet, and cool bedroom environment.", "done": False},
            {"task": "Refrain from heavy meals or caffeine after 6:00 PM.", "done": False}
        ]
    elif plan_type == "Confidence Building Plan":
        return [
            {"task": "Write down 3 things you love or appreciate about yourself.", "done": False},
            {"task": "Practice the Confidence Exercise (visualizing success).", "done": False},
            {"task": "Accomplish one small task you have been putting off.", "done": False},
            {"task": "Catch yourself in a negative self-talk moment and reframe it.", "done": False},
            {"task": "Review your list of past achievements and wins.", "done": False}
        ]
    elif plan_type == "Focus Improvement Plan":
        return [
            {"task": "Execute one 25-minute Pomodoro session with single-tasking focus.", "done": False},
            {"task": "Clear your workspace of all clutter and physical distractions.", "done": False},
            {"task": "Write down your top 3 priority tasks for the day.", "done": False},
            {"task": "Take a 5-minute offline breathing break between work blocks.", "done": False},
            {"task": "Close all browser tabs that are unrelated to your current task.", "done": False}
        ]
    return []

def render_wellness_planner(user):
    st.markdown("## 📋 Wellness Planner")
    st.markdown("*Select, generate, and complete wellness plans customized for your needs.*")
    
    # 1. Plan Generator UI
    st.markdown("### ➕ Generate a New Plan")
    st.markdown('<div class="wellness-card">', unsafe_allow_html=True)
    
    plan_options = [
        "Stress Recovery Plan", 
        "Anxiety Recovery Plan", 
        "Sleep Improvement Plan", 
        "Confidence Building Plan", 
        "Focus Improvement Plan"
    ]
    
    selected_plan_type = st.selectbox("Choose a Plan Type", plan_options)
    
    descriptions = {
        "Stress Recovery Plan": "Designed to regulate cortisol, release physiological tension, and lower daily stress levels.",
        "Anxiety Recovery Plan": "CBT-based tools targeting nervous system regulation, thought reframing, and cognitive grounding.",
        "Sleep Improvement Plan": "Mindfulness-centric actions ensuring healthy sleep hygiene, relaxation, and resting heart rates.",
        "Confidence Building Plan": "Empowerment tasks focusing on self-affirmation, positive projection, and self-esteem booster logs.",
        "Focus Improvement Plan": "Distraction-free guidelines facilitating micro-breaks, prioritization, and deep concentration."
    }
    
    st.info(descriptions[selected_plan_type])
    
    if st.button("Generate Plan ✨", use_container_width=True):
        tasks = get_default_tasks(selected_plan_type)
        plan_type_short = selected_plan_type.split()[0] # e.g. Stress, Anxiety
        
        # Save to database
        db.create_wellness_plan(
            user_id=user['id'],
            plan_type=plan_type_short,
            title=selected_plan_type,
            description=descriptions[selected_plan_type],
            tasks=tasks
        )
        st.success(f"Generated and saved your '{selected_plan_type}'! Get started below. 🌱")
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Display Active and Completed Plans
    st.markdown("### 📋 Your Current Plans")
    plans = db.get_wellness_plans(user['id'])
    
    if not plans:
        st.write("You don't have any wellness plans yet. Choose one above to start!")
        return

    active_plans = [p for p in plans if p['completed'] == 0]
    completed_plans = [p for p in plans if p['completed'] == 1]
    
    # Active Plans Section
    if active_plans:
        for plan in active_plans:
            st.markdown(f"""
            <div class="wellness-card">
                <h4>{plan['title']}</h4>
                <p style="color: #555; font-size: 14px;">{plan['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Load tasks
            tasks = json.loads(plan['tasks_json'])
            
            # Checkbox layout
            updated_tasks = []
            completed_count = 0
            
            for idx, task_item in enumerate(tasks):
                cb_key = f"plan_{plan['id']}_task_{idx}"
                checked = st.checkbox(task_item['task'], value=task_item['done'], key=cb_key)
                
                updated_tasks.append({"task": task_item['task'], "done": checked})
                if checked:
                    completed_count += 1
            
            # Calculate Progress
            progress = (completed_count / len(tasks)) * 100 if tasks else 0.0
            is_completed = 1 if progress == 100.0 else 0
            
            # Show progress bar
            st.progress(progress / 100.0)
            st.write(f"Progress: **{progress:.0f}%**")
            
            # Save progress if different
            if updated_tasks != tasks or plan['progress'] != progress or plan['completed'] != is_completed:
                db.update_wellness_plan(plan['id'], updated_tasks, progress, is_completed)
                if is_completed:
                    st.balloons()
                    st.success("Congratulations! You've completed this wellness plan. 🎉")
                st.rerun()
                
            # Option to delete
            if st.button("🗑️ Remove Plan", key=f"del_plan_{plan['id']}", type="secondary"):
                db.delete_wellness_plan(plan['id'])
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.write("No active plans currently. Create one above to guide your growth!")

    # Completed Plans Section
    if completed_plans:
        with st.expander("✅ Completed Plans Archive", expanded=False):
            for plan in completed_plans:
                st.markdown(f"""
                <div class="compact-card" style="border-left: 4px solid #6B8E23; background-color: #F8FAF5;">
                    <strong>{plan['title']}</strong> - Completed on {plan['created_at'].split()[0]} 🎉
                    <div style="font-size: 13px; color: #555; margin-top: 5px;">
                        All tasks completed successfully. Excellent dedication to your wellness journey!
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Delete Archive", key=f"del_archive_{plan['id']}"):
                    db.delete_wellness_plan(plan['id'])
                    st.rerun()

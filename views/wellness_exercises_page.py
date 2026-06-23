import streamlit as st
import time
import database.db_manager as db

def render_wellness_exercises(user):
    # Inject premium CSS styles specifically for the Breathing Exercise and visualizer
    st.markdown("""
    <style>
    /* Premium Breathing Exercise Card */
    .breathing-card-premium {
        background: linear-gradient(135deg, #F7FAF5 0%, #EAF5EC 100%) !important;
        border-radius: 24px !important;
        padding: 35px !important;
        box-shadow: 0 10px 30px rgba(46, 139, 87, 0.08) !important;
        border: 1px solid #EAF5EC !important;
        margin-bottom: 25px !important;
        text-align: center !important;
    }
    
    /* Breathing circle and transitions */
    .breathing-container-premium {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 340px;
        margin: 20px 0;
    }
    
    .breathing-circle-premium {
        border-radius: 50% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        box-shadow: 0 15px 35px rgba(46, 139, 87, 0.18) !important;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1), height 1s cubic-bezier(0.4, 0, 0.2, 1), background 1s ease-in-out !important;
        margin: auto !important;
    }
    
    .breath-action {
        font-size: 24px !important;
        font-weight: 600 !important;
        font-family: 'Playfair Display', serif !important;
    }
    
    .breath-timer {
        font-size: 32px !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
    }
    
    .motivational-message {
        font-style: italic !important;
        font-size: 18px !important;
        color: #2E8B57 !important;
        font-weight: 500 !important;
        margin: 15px 0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Target buttons inside the breathing wrapper */
    .breathing-buttons-wrapper .stButton > button {
        background-color: #2E8B57 !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 12px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(46, 139, 87, 0.25) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .breathing-buttons-wrapper .stButton > button:hover {
        background-color: #246B45 !important;
        box-shadow: 0 6px 18px rgba(46, 139, 87, 0.35) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧘 Wellness Exercises")
    st.markdown("*Practice breathing and mindfulness techniques to center yourself.*")
    
    exercise_tab, mindfulness_tab = st.tabs(["🌬️ Breathing Exercises", "🧘 Mindfulness Practices"])
    
    # Initialize session state for breathing active loop
    if "breathing_active" not in st.session_state:
        st.session_state.breathing_active = False

    # ---------------- BREATHING EXERCISES ----------------
    with exercise_tab:
        st.markdown("### Guided Breathing Timer")
        
        breathing_techniques = {
            "Box Breathing": {
                "desc": "Perfect for resetting stress. Used by athletes and first responders to regain composure.",
                "pattern": [("Inhale", 4), ("Hold", 4), ("Exhale", 4), ("Hold", 4)],
                "cycles": 5
            },
            "4-7-8 Breathing": {
                "desc": "Natural tranquilizer for the nervous system. Highly recommended for anxiety and sleep.",
                "pattern": [("Inhale", 4), ("Hold", 7), ("Exhale", 8)],
                "cycles": 4
            },
            "Deep Breathing": {
                "desc": "Simple, deep lung inflation that triggers the parasympathetic relaxation response.",
                "pattern": [("Inhale", 5), ("Exhale", 5)],
                "cycles": 5
            },
            "Calm Breathing": {
                "desc": "A gentle, paced breath ideal for maintaining daily focus and emotional equilibrium.",
                "pattern": [("Inhale", 4), ("Exhale", 4)],
                "cycles": 5
            }
        }
        
        selected_breath = st.selectbox("Choose a Breathing Technique", list(breathing_techniques.keys()))
        tech_data = breathing_techniques[selected_breath]
        
        st.markdown(f"""
        <div class="breathing-card-premium">
            <h4 style="color: #2E8B57; font-size: 22px; font-family: 'Playfair Display', serif; margin-bottom: 8px;">{selected_breath}</h4>
            <p style="color: #2F3E2E; font-size: 15px; line-height: 1.5; margin: 0;">{tech_data['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Grid layout for Visualizer and Controls
        visual_col, control_col = st.columns([1.8, 1.2])
        
        with visual_col:
            placeholder = st.empty()
            
            # Initial Idle State
            if not st.session_state.breathing_active:
                placeholder.markdown(
                    f"""
                    <div class="breathing-container-premium">
                        <div class="breathing-circle-premium" style="
                            width: 220px; 
                            height: 220px; 
                            background: radial-gradient(circle, #EAF5EC 0%, #2E8B57 100%);
                        ">
                            <span class="breath-action">Ready 🧘</span>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
        with control_col:
            if not st.session_state.breathing_active:
                st.write("Click below to start a guided session. Follow the instructions and timer displayed in the circle.")
                
                st.markdown('<div class="breathing-buttons-wrapper">', unsafe_allow_html=True)
                if st.button("🌬 Start Guided Breathing", key="start_breath_btn", use_container_width=True):
                    st.session_state.breathing_active = True
                    st.rerun()
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                
                if st.button("⭐ Save Exercise", key="save_breath_btn", use_container_width=True):
                    db.add_favorite(user['id'], "exercise", f"Breathing: {selected_breath} - {tech_data['desc']}")
                    st.toast(f"Saved {selected_breath} to Favorites! ⭐")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Show Stop button during session
                st.write("Maintain focus. You can interrupt the session at any time by stopping below.")
                st.markdown('<div class="breathing-buttons-wrapper">', unsafe_allow_html=True)
                if st.button("⏹ Stop Session", key="stop_breath_btn", use_container_width=True):
                    st.session_state.breathing_active = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Active progress parameters
                st.markdown("### Active Session")
                round_text = st.empty()
                progress_bar = st.progress(0.0)
                msg_text = st.empty()

        # Run Guided Loop if Active
        if st.session_state.breathing_active:
            total_steps = tech_data["cycles"] * sum(duration for label, duration in tech_data["pattern"])
            step_count = 0
            
            # List of motivational wellness messages
            messages = [
                "Breathe in calm.",
                "Release tension.",
                "You are safe.",
                "One breath at a time.",
                "Inhale peace, exhale stress.",
                "Let go of overthinking.",
                "Be present in this moment."
            ]
            
            for c in range(tech_data["cycles"]):
                round_text.markdown(f"**Session Progress**: Round {c+1} / {tech_data['cycles']}")
                msg_text.markdown(f'<div class="motivational-message">"{messages[c % len(messages)]}"</div>', unsafe_allow_html=True)
                
                for label, duration in tech_data["pattern"]:
                    for remaining in range(duration, 0, -1):
                        # Calculate circle dimensions
                        if label == "Inhale":
                            circle_size = 300
                            circle_bg = "radial-gradient(circle, #DDE5D0 0%, #2E8B57 100%)"
                            circle_label = "🫁 Breathe In"
                        elif label == "Hold":
                            circle_size = 300
                            circle_bg = "radial-gradient(circle, #EBF0E4 0%, #6B8E23 100%)"
                            circle_label = "⏸ Hold"
                        else:  # Exhale
                            circle_size = 180
                            circle_bg = "radial-gradient(circle, #EAF5EC 0%, #A3B18A 100%)"
                            circle_label = "🌬 Breathe Out"
                            
                        # Update progress indicator
                        step_count += 1
                        progress_val = min(1.0, float(step_count) / total_steps)
                        progress_bar.progress(progress_val)
                        
                        placeholder.markdown(
                            f"""
                            <div class="breathing-container-premium">
                                <div class="breathing-circle-premium" style="
                                    width: {circle_size}px; 
                                    height: {circle_size}px; 
                                    background: {circle_bg};
                                ">
                                    <span class="breath-action">{circle_label}</span>
                                    <span class="breath-timer">{remaining}s</span>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        time.sleep(1)
            
            # Reset and show end screen on loop completion
            st.session_state.breathing_active = False
            
            placeholder.markdown(
                f"""
                <div class="breathing-container-premium">
                    <div class="breathing-circle-premium" style="
                        width: 250px; 
                        height: 250px; 
                        background: radial-gradient(circle, #EAF5EC 0%, #2E8B57 100%);
                    ">
                        <span class="breath-action">🌿 Great Job!</span>
                        <span style="font-size: 14px; margin-top: 10px;">Exercise Complete</span>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.success("Wonderful job! You completed your breathing exercise.")
            
            # Offer restart/favorite controls in controls column
            with control_col:
                st.markdown('<div class="breathing-buttons-wrapper">', unsafe_allow_html=True)
                if st.button("🔄 Start Again", key="restart_btn", use_container_width=True):
                    st.session_state.breathing_active = True
                    st.rerun()
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("⭐ Save to Favorites", key="fav_end_btn", use_container_width=True):
                    db.add_favorite(user['id'], "exercise", f"Breathing: {selected_breath} - {tech_data['desc']}")
                    st.toast(f"Saved {selected_breath} to Favorites! ⭐")
                st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- MINDFULNESS PRACTICES ----------------
    with mindfulness_tab:
        st.markdown("### Guided Mindfulness Practices")
        
        mindfulness_options = {
            "Grounding Exercise (5-4-3-2-1)": {
                "desc": "A sensory anchoring technique to pull your mind away from anxiety and bring you back to the present.",
                "guide": """
                Follow these sensory steps slowly, taking a deep breath between each:
                1. **Look at 5 things** around you. Notice their shapes, colors, and textures (e.g., a chair, a plant, a shadow).
                2. **Feel 4 physical sensations** (e.g., the texture of your shirt, the pressure of your feet on the floor, the breeze).
                3. **Listen for 3 distinct sounds** (e.g., traffic hum, clock ticking, distant voice).
                4. **Identify 2 things you can smell** (e.g., coffee, paper, fresh air).
                5. **Acknowledge 1 thing you can taste** (even the taste of clean water or neutral state of your mouth).
                """
            },
            "Gratitude Exercise": {
                "desc": "A practice to rewire your focus towards positive elements and counter the brain's natural negativity bias.",
                "guide": """
                Take a few minutes to write or reflect on three things you are grateful for today. They don't have to be grand:
                - *Example: A hot cup of tea, a text from a friend, a warm blanket.*
                
                Reflect on *why* these things brought you comfort. Writing them down cements the positive emotion in your memory pathways.
                """
            },
            "Confidence Exercise (Success Anchoring)": {
                "desc": "A technique to boost self-efficacy, relieve imposter syndrome, and alleviate exam or placement anxiety.",
                "guide": """
                Close your eyes and stand or sit tall:
                1. **Recall a moment** in your past when you felt proud, capable, or successful.
                2. **Visualize the scene** in rich detail: What were you wearing? Who was there? What did you hear?
                3. **Reconnect with that feeling** of accomplishment and ease.
                4. **Clench your fist** gently as you recall that peak sensation. This is your physical 'anchor'.
                5. Open your hands and repeat: *"I have succeeded before, and I have the skills to navigate this moment too."*
                """
            },
            "Sleep Relaxation (Progressive Muscle Relaxation)": {
                "desc": "Deep muscle scanning designed to systematically release physical stress and prepare the body for deep sleep.",
                "guide": """
                Lie down comfortably in a quiet, dark room:
                1. **Tense and release your toes**: Curl them tightly for 5 seconds, then let them go completely flaccid.
                2. **Squeeze your calves and thighs**: Flex these muscles, hold for 5 seconds, then release. Feel the blood flow return.
                3. **Tighten your stomach and chest**: Take a deep breath, brace your core, hold, and release with a long exhale.
                4. **Clench your fists and shoulders**: Pull shoulders up to ears, squeeze hands, then drop them heavily into the mattress.
                5. **Squeeze facial muscles**: Screw up eyes and jaw, hold, and let your face soften completely. Breathe normally.
                """
            }
        }
        
        selected_mind = st.selectbox("Choose a Mindfulness Practice", list(mindfulness_options.keys()))
        mind_data = mindfulness_options[selected_mind]
        
        st.markdown(f"""
        <div class="wellness-card">
            <h4>{selected_mind}</h4>
            <p style="font-style: italic; color: #555;">{mind_data['desc']}</p>
            <hr>
            <div style="font-size: 15px; line-height: 1.6; white-space: pre-line;">
                {mind_data['guide']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Save Mindfulness Exercise to Favorites
        if st.button("⭐ Save Practice to Favorites", key="fav_mind"):
            db.add_favorite(user['id'], "exercise", f"Mindfulness: {selected_mind} - {mind_data['desc']}")
            st.toast(f"Saved {selected_mind} to Favorites! ⭐")
            
        # Specific interactive segment for Gratitude Journal
        if "Gratitude" in selected_mind:
            st.markdown("#### Log a Quick Gratitude Note")
            g_note = st.text_area("Write one thing you are grateful for right now:", placeholder="Today, I am grateful for...")
            if st.button("Save Gratitude Note 📝"):
                if g_note:
                    db.add_favorite(user['id'], "quote", f"Gratitude: {g_note}")
                    st.success("Saved to your Favorites list! 🌿")
                else:
                    st.warning("Please write something first.")

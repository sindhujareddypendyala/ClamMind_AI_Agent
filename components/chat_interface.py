from streamlit.proto import ColorPicker_pb2
import streamlit as st
import database.db_manager as db
from services.agent_pipeline import run_agent_pipeline
from services.voice_service import transcribe_audio, text_to_speech
from datetime import datetime

def send_user_message(user, conversation_id, message_text):
    """
    Utility function to submit user message, run agents, and reload chat.
    """
    if not message_text.strip():
        return
        
    # Save user message to database
    db.add_message(conversation_id, "user", message_text)
    
    # Auto-rename conversation based on the first message
    import re
    messages = db.get_conversation_messages(conversation_id)
    if len(messages) == 1:
        clean_text = re.sub(r'[^\w\s]', '', message_text)
        words = [w.capitalize() for w in clean_text.split()[:3]]
        if words:
            new_title = " ".join(words)
            if len(new_title) > 25:
                new_title = new_title[:22] + "..."
            db.rename_conversation(conversation_id, new_title)
    
    # Run multi-agent pipeline
    with st.spinner("CalmMind is reflecting..."):
        pipeline_result = run_agent_pipeline(user['id'], conversation_id, message_text)
        db.add_message(conversation_id, "assistant", pipeline_result['content'])
        
        # Save last detected state to trigger smart recommendation buttons
        st.session_state.last_detected_emotion = pipeline_result.get('emotion', 'neutral')
        st.session_state.last_recommended_plan = pipeline_result.get('plan', '')
        
        # If voice output is enabled, synthesize audio
        if st.session_state.get("voice_output_enabled", False) and not pipeline_result.get('blocked', False):
            audio_path = text_to_speech(pipeline_result['content'])
            if audio_path:
                st.session_state.play_audio_path = audio_path
                
    # Clear input state
    st.session_state.user_text_input = ""
    st.rerun()

def render_chat_interface(user):
    # Initialize session state for chat onboarding flow
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False

    # STEP 1: LANDING PAGE
    if not st.session_state.chat_started:
        st.markdown("<div class='landing-container'>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1.2, 1], gap="large")

        with col_left:
            st.markdown("""
            <div class="hero-left">
                <h1 style="color: #2E8B57; font-family: 'Playfair Display', serif; font-size: 48px; margin-bottom: 10px;">🧠 CalmMind AI</h1>
                <h3 style="color: #6B8E23; font-family: 'Inter', sans-serif; font-size: 22px; margin-bottom: 20px; font-weight: 500;">Your Personal Mental Wellness Companion</h3>
                <p style="font-size: 16px; line-height: 1.6; color: #2F3E2E; margin-bottom: 15px;">
                    CalmMind AI helps users manage:
                </p>
                <ul style="font-size: 16px; line-height: 1.8; color: #2F3E2E; margin-bottom: 25px; padding-left: 20px;">
                    <li>Stress</li>
                    <li>Anxiety</li>
                    <li>Overthinking</li>
                    <li>Emotional Wellness</li>
                    <li>Motivation</li>
                    <li>Daily Wellbeing</li>
                </ul>
                <p style="font-size: 16px; line-height: 1.6; color: #2F3E2E; margin-bottom: 30px;">
                    through AI-powered conversations and personalized wellness recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Start Chat", key="landing_start_chat_btn", use_container_width=True):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_conv_id = db.create_conversation(user['id'], f"Session - {now_str}")
                st.session_state.conversation_id = new_conv_id
                st.session_state.chat_started = True
                st.rerun()

        with col_right:
            st.markdown('<div class="hero-image-card" style="border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); overflow: hidden; background: white;">', unsafe_allow_html=True)
            import os
            image_path = os.path.join("assets", "wellness_hero.png")
            st.image(image_path, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # STEP 2: HOME PAGE (Wellness Chat Companion)
    # Initialize Conversation if None
    if not st.session_state.get("conversation_id"):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        conv_id = db.create_conversation(user['id'], f"Session - {now_str}")
        st.session_state.conversation_id = conv_id

    conversation_id = st.session_state.conversation_id

    # 1. Top Header & Subtitle
    st.markdown("""
    <div class="chat-header">
        <h1 class="chat-title">🌿 Wellness Chat Companion</h1>
        <p class="chat-subtitle">Talk through your thoughts in a safe space.</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Quick Action Buttons (Placed right below the header)
    col_qa1, col_qa2, col_qa3, col_qa4, col_qa5 = st.columns(5)
    with col_qa1:
        st.markdown('<div class="quick-action-btn">', unsafe_allow_html=True)
        if st.button("😰 I'm Stressed", key="qa_stressed", use_container_width=True):
            send_user_message(user, conversation_id, "I'm feeling stressed")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_qa2:
        st.markdown('<div class="quick-action-btn">', unsafe_allow_html=True)
        if st.button("🤯 I'm Overthinking", key="qa_overthinking", use_container_width=True):
            send_user_message(user, conversation_id, "I'm overthinking")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_qa3:
        st.markdown('<div class="quick-action-btn">', unsafe_allow_html=True)
        if st.button("😴 Help Me Sleep", key="qa_sleep", use_container_width=True):
            send_user_message(user, conversation_id, "Help me sleep")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_qa4:
        st.markdown('<div class="quick-action-btn">', unsafe_allow_html=True)
        if st.button("💪 Motivate Me", key="qa_motivate", use_container_width=True):
            send_user_message(user, conversation_id, "Motivate me")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_qa5:
        st.markdown('<div class="quick-action-btn">', unsafe_allow_html=True)
        if st.button("❤️ Emotional Support", key="qa_support", use_container_width=True):
            send_user_message(user, conversation_id, "I need emotional support")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='chat-divider'></div>", unsafe_allow_html=True)

    # 3. Display Chat Messages (ChatGPT-style Layout)
    messages = db.get_conversation_messages(conversation_id)
    
    # Wrap all messages in a container for styling
    st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
    for idx, msg in enumerate(messages):
        role = msg['role']
        avatar = "🌿" if role == "assistant" else None
        
        with st.chat_message(role, avatar=avatar):
            if role == "assistant":
                # Render content with action icons inside bubble
                col_text, col_icons = st.columns([12, 1])
                with col_text:
                    st.markdown(msg['content'])
                with col_icons:
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        if st.button("☆", key=f"fav_star_{msg['id']}", help="Save to Favorites"):
                            db.add_favorite(user['id'], "response", msg['content'])
                            st.toast("Saved to Favorites! ⭐")
                    with col_s2:
                        st.markdown("<span style='color: #7A8F75; cursor: pointer; font-size: 16px; font-weight: bold;'>⋮</span>", unsafe_allow_html=True)
            else:
                st.markdown(msg['content'])
            
            # Message Timestamp at bottom
            formatted_time = ""
            try:
                clean_time = msg['created_at'].split()[1][:5]
                formatted_time = clean_time
            except:
                formatted_time = datetime.now().strftime("%H:%M")
            
            st.markdown(f'<div class="chat-timestamp">{formatted_time}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Render Smart Recommendation Buttons under the latest message (if appropriate)
    if messages:
        last_emotion = st.session_state.get("last_detected_emotion", "neutral")
        last_plan = st.session_state.get("last_recommended_plan", "")
        last_msg_text = messages[-1]['content'].lower()
        
        is_stress = (last_emotion in ["stressed", "overwhelmed", "anxious", "angry"] or "stress" in last_msg_text or "anxi" in last_msg_text or "nervous" in last_msg_text)
        is_sleep = (last_emotion in ["tired"] or "sleep" in last_msg_text or "insomnia" in last_msg_text or "awake" in last_msg_text)
        is_burnout = ("burnout" in last_msg_text or "exhausted" in last_msg_text or "weary" in last_msg_text or last_plan == "Stress Recovery Plan")

        if is_stress or is_sleep or is_burnout:
            st.markdown("<br>", unsafe_allow_html=True)
            col_rec1, col_rec2, col_rec3, col_rec4 = st.columns(4)
            
            with col_rec1:
                if is_stress:
                    st.markdown('<div class="recommendation-pill">', unsafe_allow_html=True)
                    if st.button("🌬 Start Breathing Exercise", key="rec_breath_btn", use_container_width=True):
                        st.session_state.page = "exercises"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            with col_rec2:
                if is_sleep:
                    st.markdown('<div class="recommendation-pill">', unsafe_allow_html=True)
                    if st.button("😴 Sleep Exercise", key="rec_sleep_btn", use_container_width=True):
                        st.session_state.page = "exercises"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            with col_rec3:
                if is_burnout:
                    st.markdown('<div class="recommendation-pill">', unsafe_allow_html=True)
                    if st.button("📋 Recovery Plan", key="rec_plan_btn", use_container_width=True):
                        st.session_state.page = "planner"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            with col_rec4:
                st.markdown('<div class="recommendation-pill">', unsafe_allow_html=True)
                if st.button("💚 I'm Here To Talk", key="rec_talk_btn", use_container_width=True):
                    st.toast("I am listening. Share anything on your mind.")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 5. VOICE INPUT & CHAT INPUT (Unified ChatGPT-style layout)
    if "show_voice_recorder" not in st.session_state:
        st.session_state.show_voice_recorder = False

    # Injected styles for the premium ChatGPT-style input bar
    st.markdown("""
    <style>
    .chat-input-wrapper-new {
        background-color: white !important;
        border: 1.5px solid #EBF0E4 !important;
        border-radius: 18px !important;
        padding: 6px 12px 6px 20px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 4px 20px rgba(107, 142, 35, 0.08) !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
        width: 100% !important;
        height: 56px !important;
    }
    
    .chat-input-wrapper-new [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
    }

    .chat-input-wrapper-new div[data-testid="stTextInput"] {
        flex-grow: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
    }
    .chat-input-wrapper-new div[data-testid="stTextInput"] fieldset {
        border: none !important;
    }
    .chat-input-wrapper-new div[data-testid="stTextInput"] input {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        box-shadow: none !important;
        color: #2F3E2E !important;
        font-size: 16px !important;
        height: 44px !important;
    }

    /* Style the icons inside input bar */
    .chat-input-wrapper-new .stButton > button {
        background-color: transparent !important;
        color: #6B8E23 !important; /* Olive green accent */
        border: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        margin: 0 !important;
    }

    .chat-input-wrapper-new .stButton > button:hover {
        background-color: #F7FAF5 !important;
        color: #2E8B57 !important;
        transform: scale(1.05);
    }

    /* Voice Modal Card */
    .voice-modal-card {
        background: linear-gradient(135deg, #F7FAF5 0%, #EAF5EC 100%) !important;
        border-radius: 18px !important;
        padding: 24px !important;
        border: 1px solid #DDE5D0 !important;
        box-shadow: 0 8px 30px rgba(107, 142, 35, 0.1) !important;
        margin-bottom: 20px !important;
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # Voice Recorder Modal Popup
    if st.session_state.show_voice_recorder:
        st.markdown("""
        <div class="voice-modal-card">
            <h4 style="color: #2E8B57; font-family: 'Playfair Display', serif; font-size: 20px; margin-bottom: 5px;">🎙️ Speak to CalmMind</h4>
            <p style="color: #7A8F75; font-size: 13px; margin-bottom: 15px;">Your recording will be transcribed and automatically added to the chat input field.</p>
        </div>
        """, unsafe_allow_html=True)
        
        audio_file = st.audio_input("Record voice", key="voice_recorder_input", label_visibility="collapsed")
        
        col_close1, col_close2 = st.columns([1, 1])
        with col_close2:
            if st.button("Cancel", key="cancel_voice_btn", use_container_width=True):
                st.session_state.show_voice_recorder = False
                st.rerun()
                
        if audio_file:
            audio_bytes = audio_file.read()
            with st.spinner("Transcribing your thoughts..."):
                transcribed = transcribe_audio(audio_bytes)
            if transcribed:
                st.session_state.chat_text_input = transcribed
                st.toast("Transcribed successfully! 🌿")
            st.session_state.show_voice_recorder = False
            st.rerun()
            
        st.markdown("<div class='chat-divider'></div>", unsafe_allow_html=True)

    # Render unified ChatGPT-style layout
    st.markdown('<div class="chat-input-wrapper-new">', unsafe_allow_html=True)
    input_cols = st.columns([12, 1, 1])
    with input_cols[0]:
        user_message = st.text_input("How are you feeling today?", label_visibility="collapsed", key="chat_text_input", placeholder="How are you feeling today?")
    with input_cols[1]:
        mic_clicked = st.button("🎤", key="trigger_voice_modal_btn")
    with input_cols[2]:
        send_clicked = st.button("➤", key="chat_send_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    # Open voice modal
    if mic_clicked:
        st.session_state.show_voice_recorder = True
        st.rerun()

    # Process text input (either by Enter key or by Send button click)
    text_to_send = ""
    if user_message:
        text_to_send = user_message
    elif send_clicked and st.session_state.get("chat_text_input"):
        text_to_send = st.session_state.chat_text_input

    if text_to_send:
        send_user_message(user, conversation_id, text_to_send)

    # 6. PLAY AUDIO RESPONSE (If voice output enabled)
    if st.session_state.get("play_audio_path"):
        audio_path = st.session_state.play_audio_path
        st.session_state.play_audio_path = None
        st.audio(audio_path, format="audio/mp3", autoplay=True)

    # 7. AUTO SCROLL & DISCLAIMER
    js = """
    <script>
    window.scrollTo(0, document.body.scrollHeight);
    </script>
    """
    st.components.v1.html(js, height=0)
    
    st.markdown(
        """
        <div class="chat-disclaimer">
            CalmMind AI is not a substitute for professional medical advice, diagnosis, or treatment.
            If you are in crisis, please seek help from a qualified professional. You are not alone 💚
        </div>
        """,
        unsafe_allow_html=True
    )


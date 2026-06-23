import streamlit as st
import database.db_manager as db
from datetime import datetime

def render_sidebar(user):
    # Inject premium CSS styles specifically for the sidebar overrides
    st.sidebar.markdown("""
    <style>
    /* Sidebar container styling */
    section[data-testid="stSidebar"] {
        background-color: #F7FAF5 !important;
        border-right: 1px solid #DDE5D0 !important;
    }
    
    /* Header layout styling */
    .sidebar-header {
        padding: 10px 5px;
        margin-bottom: 10px;
    }
    
    .sidebar-header h2 {
        color: #2E8B57 !important;
        font-family: "Playfair Display", serif;
        font-size: 26px !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
    }
    
    .sidebar-header p {
        color: #6B8E23 !important;
        font-family: "Inter", sans-serif;
        font-size: 14px !important;
        line-height: 1.4 !important;
        margin: 0 !important;
    }

    /* Dividers and grouping titles */
    .sidebar-divider {
        border-top: 1px solid #DDE5D0;
        margin: 15px 0;
    }

    .sidebar-section-title {
        color: #6B8E23 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.8px;
        margin: 18px 5px 8px 5px;
        font-family: "Inter", sans-serif;
    }
    
    .sidebar-history-category {
        color: #2F3E2E !important;
        font-size: 12px !important;
        font-weight: 600;
        margin: 10px 5px 4px 5px;
    }

    /* Sidebar Button defaults */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #2F3E2E !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    
    /* Hover effects */
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #EBF0E4 !important;
        color: #2E8B57 !important;
        transform: translateX(2px);
    }
    
    /* Active button styling */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #2E8B57 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #246B43 !important;
        color: #FFFFFF !important;
    }
    
    /* Footer pinning */
    .sidebar-footer {
        border-top: 1px solid #DDE5D0;
        padding-top: 15px;
        margin-top: 35px;
        text-align: center;
        font-size: 11px;
        color: #7A8F75;
        font-family: "Inter", sans-serif;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Top Section - Welcoming
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>🌿 CalmMind AI</h2>
        <p>Welcome back,<br><strong>{name}</strong> 👋</p>
    </div>
    """.format(name=user['name']), unsafe_allow_html=True)
    
    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # 2. New Chat Button
    if st.sidebar.button("➕ New Chat", use_container_width=True, key="sidebar_new_chat_btn", type="primary"):
        # Create a new conversation in the database
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_title = f"Session - {now_str}"
        conv_id = db.create_conversation(user['id'], new_title)
        st.session_state.conversation_id = conv_id
        st.session_state.page = "chat"
        st.rerun()

    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # 3. Main Navigation
    if st.sidebar.button("💬 AI Companion", use_container_width=True, type="primary" if st.session_state.page == "chat" else "secondary", key="sidebar_ai_companion_btn"):
        st.session_state.page = "chat"
        st.rerun()

    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # 4. Wellness Tools Section
    st.sidebar.markdown("<p class='sidebar-section-title'>🌱 Wellness Tools</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("📋 Wellness Planner", use_container_width=True, type="primary" if st.session_state.page == "planner" else "secondary", key="sidebar_planner_btn"):
        st.session_state.page = "planner"
        st.rerun()
        
    if st.sidebar.button("📈 Mood Tracker", use_container_width=True, type="primary" if st.session_state.page == "tracker" else "secondary", key="sidebar_tracker_btn"):
        st.session_state.page = "tracker"
        st.rerun()
        
    if st.sidebar.button("🧘 Wellness Exercises", use_container_width=True, type="primary" if st.session_state.page == "exercises" else "secondary", key="sidebar_exercises_btn"):
        st.session_state.page = "exercises"
        st.rerun()
        
    if st.sidebar.button("🔮 Mood Prediction", use_container_width=True, type="primary" if st.session_state.page == "prediction" else "secondary", key="sidebar_prediction_btn"):
        st.session_state.page = "prediction"
        st.rerun()

    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # 5. History Section
    st.sidebar.markdown("<p class='sidebar-section-title'>🕒 History</p>", unsafe_allow_html=True)
    conversations = db.get_conversations(user['id'])
    
    def get_date_category(created_at_str):
        try:
            clean_date = created_at_str.split(".")[0]
            dt = datetime.strptime(clean_date, "%Y-%m-%d %H:%M:%S")
        except:
            try:
                dt = datetime.strptime(created_at_str, "%Y-%m-%d")
            except:
                return "Previous Days"
        
        today = datetime.utcnow().date()
        delta = (today - dt.date()).days
        if delta == 0:
            return "Today"
        elif delta == 1:
            return "Yesterday"
        else:
            return "Previous Days"

    if conversations:
        grouped = {"Today": [], "Yesterday": [], "Previous Days": []}
        for conv in conversations[:10]:
            cat = get_date_category(conv['created_at'])
            grouped[cat].append(conv)
            
        for category in ["Today", "Yesterday", "Previous Days"]:
            if grouped[category]:
                st.sidebar.markdown(f"<p class='sidebar-history-category'>{category}</p>", unsafe_allow_html=True)
                for conv in grouped[category]:
                    conv_title = conv['title']
                    if len(conv_title) > 22:
                        conv_title = conv_title[:20] + "..."
                        
                    col1, col2 = st.sidebar.columns([5, 1])
                    with col1:
                        is_active = (st.session_state.page == "chat" and st.session_state.conversation_id == conv['id'])
                        if st.button(
                            f"💬 {conv_title}", 
                            key=f"conv_{conv['id']}", 
                            use_container_width=True,
                            type="primary" if is_active else "secondary"
                        ):
                            st.session_state.conversation_id = conv['id']
                            st.session_state.page = "chat"
                            st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"del_conv_{conv['id']}", help="Delete"):
                            db.delete_conversation(conv['id'])
                            if st.session_state.conversation_id == conv['id']:
                                st.session_state.conversation_id = None
                            st.rerun()
    else:
        st.sidebar.write("No conversations yet.")

    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # 6. Favorites
    if st.sidebar.button("⭐ Favorites", use_container_width=True, type="primary" if st.session_state.page == "favorites" else "secondary", key="sidebar_favorites_btn"):
        st.session_state.page = "favorites"
        st.rerun()

    st.sidebar.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    # 7. Settings Section
    st.sidebar.markdown("<p class='sidebar-section-title'>⚙ Settings</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("👤 Edit Profile", use_container_width=True, type="primary" if st.session_state.page == "profile" else "secondary", key="sidebar_profile_btn"):
        st.session_state.page = "profile"
        st.rerun()
        
    if st.sidebar.button("📤 Export Data", use_container_width=True, type="primary" if st.session_state.page == "export" else "secondary", key="sidebar_export_btn"):
        st.session_state.page = "export"
        st.rerun()
        
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="sidebar_logout_btn"):
        st.session_state.clear()
        st.session_state.logged_out = True
        st.rerun()

    # Footer
    st.sidebar.markdown("""
    <div class="sidebar-footer">
        Built by<br>
        <strong>Sindhuja Reddy Pendyala</strong><br><br>
        Built for GenAI Internship 💚
    </div>
    """, unsafe_allow_html=True)


   
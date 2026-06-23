import streamlit as st
import os

import database.db_manager as db

from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface

from views.mood_tracker_page import render_mood_tracker
from views.wellness_planner_page import render_wellness_planner
from views.wellness_exercises_page import render_wellness_exercises
from views.mood_prediction_page import render_mood_prediction
from views.favorites_page import render_favorites
from views.settings_page import (
    render_edit_profile,
    render_export_data
)

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="CalmMind AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# HIDE STREAMLIT DEFAULT UI
# -----------------------------------

st.markdown("""
<style>

section[data-testid="stSidebarNav"]{
    display:none;
}

#MainMenu{
    visibility:hidden;
}

header{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# DATABASE
# -----------------------------------

db.init_db()

# -----------------------------------
# LOAD CSS
# -----------------------------------

css_path = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "styles.css"
)

if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "page" not in st.session_state:
    st.session_state.page = "chat"

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "show_profile_form" not in st.session_state:
    st.session_state.show_profile_form = False

if "logged_out" not in st.session_state:
    st.session_state.logged_out = False

# -----------------------------------
# USER AUTO-LOGIN & SESSION
# -----------------------------------

user = None

if "app_started" not in st.session_state:
    # Auto-login if a user profile already exists in the database
    existing_user = db.get_user()
    if existing_user and not st.session_state.get("logged_out", False):
        st.session_state.app_started = True
    else:
        st.session_state.app_started = False

if st.session_state.app_started:
    user = db.get_user()

# ===================================
# LANDING PAGE
# ===================================

if not user:

    if not st.session_state.show_profile_form:

        # Full-screen split layout for Landing Page
        st.markdown("<div class='landing-container'>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1.2, 1], gap="large")

        with col_left:
            st.markdown("""
            <div class="hero-left">
                <div class="hero-logo">🧠</div>
                <h1 class="hero-title">CalmMind AI</h1>
                <h3 class="hero-subtitle">Your Personal Mental Wellness Companion</h3>
                <p class="hero-description">
                    CalmMind AI helps you manage stress, anxiety, overthinking, emotional wellness, motivation, and daily wellbeing through AI-powered conversations and personalized wellness recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Start Chat", key="hero_start_chat_btn", use_container_width=True):
                st.session_state.show_profile_form = True
                st.rerun()

        with col_right:
            st.markdown('<div class="hero-image-card">', unsafe_allow_html=True)
            image_path = os.path.join("assets", "wellness_hero.png")
            st.image(image_path, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    else:

        # Centered onboarding card for Profile Page
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1.5, 1])

        with c2:
            st.markdown("""
            <div class="onboarding-card">
                <div class="onboarding-header">
                    <h2>Create Your Profile</h2>
                    <p>Customize your experience on CalmMind AI</p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("profile_form"):
                name = st.text_input("Full Name", placeholder="Enter your full name")
                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=120,
                    value=20
                )
                occupation = st.text_input(
                    "Occupation",
                    placeholder="e.g. Student, Software Developer"
                )

                submitted = st.form_submit_button(
                    "Continue to CalmMind",
                    use_container_width=True
                )
                if submitted:
                    if name.strip():
                        db.create_user(
                            name.strip(),
                            age,
                            occupation.strip()
                        )
                        st.success("Welcome to CalmMind 🌿")
                        st.session_state.show_profile_form = False
                        st.session_state.app_started = True
                        st.session_state.logged_out = False
                        st.rerun()
                    else:
                        st.error("Please enter your name.")
            st.markdown("</div>", unsafe_allow_html=True)

# ===================================
# MAIN APP
# ===================================

else:

    render_sidebar(user)

    page = st.session_state.page

    if page == "chat":
        render_chat_interface(user)

    elif page == "planner":
        render_wellness_planner(user)

    elif page == "tracker":
        render_mood_tracker(user)

    elif page == "exercises":
        render_wellness_exercises(user)

    elif page == "prediction":
        render_mood_prediction(user)

    elif page == "favorites":
        render_favorites(user)

    elif page == "profile":
        render_edit_profile(user)

    elif page == "export":
        render_export_data(user)
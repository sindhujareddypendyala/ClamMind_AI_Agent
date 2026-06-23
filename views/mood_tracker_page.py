import streamlit as st
import database.db_manager as db
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def render_mood_tracker(user):
    st.markdown("## 📈 Mood Tracker")
    st.markdown("*Log your mental states and visualize patterns over time.*")
    
    # 1. Log Mood Form
    with st.expander("📝 Log Your Current State", expanded=True):
        st.markdown('<div class="wellness-card">', unsafe_allow_html=True)
        with st.form("mood_log_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                mood = st.selectbox(
                    "Current Mood",
                    ["Calm", "Happy", "Neutral", "Stressed", "Anxious", "Sad", "Angry", "Tired", "Overwhelmed", "Lonely"]
                )
                stress_level = st.slider("Stress Level (1 = Low, 10 = High)", 1, 10, 5)
                anxiety_level = st.slider("Anxiety Level (1 = Low, 10 = High)", 1, 10, 5)
                
            with col2:
                energy_level = st.slider("Energy Level (1 = Low, 10 = High)", 1, 10, 5)
                sleep_hours = st.number_input("Sleep Hours last night", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
                trigger = st.text_input("Key Trigger (e.g. Exams, Work, Family, None)", placeholder="What contributed to this mood?")
                
            notes = st.text_area("Personal Notes / Journal Entry", placeholder="How are you feeling? Write down your thoughts...")
            
            submit_btn = st.form_submit_button("Log My Mood 📈")
            
            if submit_btn:
                db.log_mood(
                    user_id=user['id'],
                    mood=mood,
                    stress_level=stress_level,
                    anxiety_level=anxiety_level,
                    energy_level=energy_level,
                    sleep_hours=sleep_hours,
                    trigger=trigger if trigger else "None",
                    notes=notes if notes else ""
                )
                st.success("Mood logged successfully! Check the trends below. 🌿")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Mood Trends and Visualizations
    st.markdown("### 📊 Your Wellness Trends")
    
    # Fetch mood logs (last 30 entries)
    logs = db.get_mood_logs(user['id'], days=30)
    
    if not logs:
        st.info("Log your mood above to unlock trends and insights! 📈")
        return
        
    df = pd.DataFrame(logs)
    
    # Preprocess date format for charting
    df['date'] = pd.to_datetime(df['created_at']).dt.strftime('%b %d, %H:%M')
    
    # Tabbed view for different charts
    tab1, tab2, tab3 = st.tabs(["Stress & Anxiety", "Energy & Sleep", "Logged Entries"])
    
    with tab1:
        st.markdown("#### Stress vs Anxiety Over Time")
        fig = go.Figure()
        
        # Stress line
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df['stress_level'],
            mode='lines+markers',
            name='Stress Level',
            line=dict(color='#6B8E23', width=3), # Primary Olive Green
            marker=dict(size=8)
        ))
        
        # Anxiety line
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df['anxiety_level'],
            mode='lines+markers',
            name='Anxiety Level',
            line=dict(color='#C27D38', width=3), # Secondary Warm Accent
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title='Level (1-10)', range=[0, 11], gridcolor='#EBF0E4'),
            xaxis=dict(gridcolor='#EBF0E4', tickangle=45),
            margin=dict(l=40, r=40, t=20, b=40),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.markdown("#### Sleep vs Energy")
        fig2 = go.Figure()
        
        # Energy line
        fig2.add_trace(go.Scatter(
            x=df['date'], 
            y=df['energy_level'],
            mode='lines+markers',
            name='Energy Level (1-10)',
            line=dict(color='#A3B18A', width=3),
            marker=dict(size=8)
        ))
        
        # Sleep line (secondary y-axis or separate line)
        fig2.add_trace(go.Scatter(
            x=df['date'], 
            y=df['sleep_hours'],
            mode='lines+markers',
            name='Sleep Hours',
            line=dict(color='#4A708B', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title='Value', range=[0, 24], gridcolor='#EBF0E4'),
            xaxis=dict(gridcolor='#EBF0E4', tickangle=45),
            margin=dict(l=40, r=40, t=20, b=40),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    with tab3:
        st.markdown("#### History of Logs")
        
        # Reverse list to show newest logs on top
        df_display = df.iloc[::-1].copy()
        
        for idx, row in df_display.iterrows():
            st.markdown(f"""
            <div class="compact-card">
                <div style="display: flex; justify-content: space-between;">
                    <strong>Mood: {row['mood']}</strong>
                    <span style="color: #7A8F75; font-size: 13px;">{row['created_at']}</span>
                </div>
                <div style="margin-top: 8px; font-size: 14px;">
                    <span>Stress: <strong>{row['stress_level']}/10</strong> | </span>
                    <span>Anxiety: <strong>{row['anxiety_level']}/10</strong> | </span>
                    <span>Energy: <strong>{row['energy_level']}/10</strong> | </span>
                    <span>Sleep: <strong>{row['sleep_hours']}h</strong></span>
                </div>
                <div style="margin-top: 5px; font-size: 14px;">
                    <strong>Trigger:</strong> {row['trigger']}
                </div>
                {f'<div style="margin-top: 5px; font-size: 14px; font-style: italic; color: #555;">"{row["notes"]}"</div>' if row['notes'] else ''}
            </div>
            """, unsafe_allow_html=True)

import streamlit as st
import database.db_manager as db
import plotly.graph_objects as go
from agents.mood_prediction_agent import analyze_mood_trends
import re

def extract_confidence_percentage(text):
    """
    Tries to find a percentage number (e.g. 75%) inside the Gemini response text
    to render on a visual gauge. Defaults to 50% if not found.
    """
    matches = re.findall(r'(\d+)\s*%', text)
    if matches:
        # Return the first percentage found
        val = int(matches[0])
        if 0 <= val <= 100:
            return val
    return 65 # reasonable neutral default

def render_mood_prediction(user):
    st.markdown("## 🔮 Mood Prediction & Insights")
    st.markdown("*AI-driven forecasting and analytics based on your logs.*")
    
    # 1. Select Timeline Range
    st.markdown('<div class="compact-card">', unsafe_allow_html=True)
    col_range, col_info = st.columns([1, 2])
    with col_range:
        range_days = st.selectbox(
            "Select Analysis Window",
            [7, 14, 30],
            format_func=lambda x: f"Last {x} Days"
        )
    with col_info:
        st.write("The AI analyzing agent processes your mood, stress, energy, triggers, and sleep data to predict potential stress patterns and offer preventative self-care.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Trigger Prediction Analysis
    with st.spinner("Analyzing log parameters and running models..."):
        analysis_result = analyze_mood_trends(user['id'], days=range_days)
        
    if not analysis_result["success"]:
        st.warning(analysis_result["message"])
        return
        
    # 3. Render Dashboard Indicators
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Logs Analyzed", f"{analysis_result['logs_count']} Entries")
    with col2:
        # Determine delta icon / color
        st.metric("Avg Stress Level", f"{analysis_result['avg_stress']}/10", help=analysis_result['stress_trend'])
    with col3:
        st.metric("Avg Sleep", f"{analysis_result['avg_sleep']} hrs", help=f"Energy: {analysis_result['avg_energy']}/10")
        
    # Render trends status cards
    st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 20px;">
        <div style="flex: 1; padding: 15px; background-color: #FFFFFF; border-radius: 12px; border: 1px solid #EBF0E4; text-align: center;">
            <span style="font-size: 14px; color: #777;">Stress Trend</span><br>
            <strong>{analysis_result['stress_trend']}</strong>
        </div>
        <div style="flex: 1; padding: 15px; background-color: #FFFFFF; border-radius: 12px; border: 1px solid #EBF0E4; text-align: center;">
            <span style="font-size: 14px; color: #777;">Anxiety Trend</span><br>
            <strong>{analysis_result['anxiety_trend']}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Render Confidence Gauge
    confidence_val = extract_confidence_percentage(analysis_result['analysis'])
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence_val,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Predicted Coping Capacity (Confidence %)", 'font': {'size': 18, 'family': 'Outfit'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#2F3E2E"},
            'bar': {'color': "#6B8E23"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#DDE5D0",
            'steps': [
                {'range': [0, 40], 'color': '#F4DCD6'},
                {'range': [40, 70], 'color': '#FDF5E2'},
                {'range': [70, 100], 'color': '#E8F0DC'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': confidence_val
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220,
        margin=dict(l=20, r=20, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. Render Detailed Analysis Text
    st.markdown("### 📋 Detailed AI Insights")
    st.markdown(f"""
    <div class="wellness-card" style="line-height: 1.6; font-size: 15px; white-space: pre-line;">
        {analysis_result['analysis']}
    </div>
    """, unsafe_allow_html=True)
    
    # Save Insights to Favorites
    if st.button("⭐ Save Insights to Favorites"):
        db.add_favorite(
            user['id'], 
            "quote", 
            f"CalmMind AI Prediction (Last {range_days} days): "
            f"Avg Stress: {analysis_result['avg_stress']}/10. Coping: {confidence_val}%. "
            f"Insight: {analysis_result['analysis'][:150]}..."
        )
        st.toast("Saved prediction report summary to Favorites! ⭐")

import streamlit as st
import database.db_manager as db

def render_favorites(user):
    st.markdown("## ⭐ Favorites")
    st.markdown("*Your curated library of supportive messages, helpful exercises, and insights.*")
    
    favs = db.get_favorites(user['id'])
    
    if not favs:
        st.info("You haven't saved any items to your favorites yet. Click the '⭐ Favorite' button in chats or exercises to save items here! 🌿")
        return
        
    # Group favorites by type
    quotes = [f for f in favs if f['type'] in ['quote', 'response']]
    exercises = [f for f in favs if f['type'] == 'exercise']
    plans = [f for f in favs if f['type'] == 'plan']
    
    tab1, tab2 = st.tabs(["💬 Saved Responses & Quotes", "🧘 Saved Exercises & Plans"])
    
    with tab1:
        st.markdown("### Saved Reflections & Insights")
        if quotes:
            for item in quotes:
                st.markdown(f"""
                <div class="wellness-card" style="border-left: 4px solid #A3B18A;">
                    <div style="font-size: 15px; line-height: 1.6; white-space: pre-line;">
                        {item['content']}
                    </div>
                    <div style="font-size: 11px; color: #7A8F75; margin-top: 10px; text-align: right;">
                        Saved on: {item['saved_at']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Remove", key=f"del_fav_{item['id']}", type="secondary"):
                    db.delete_favorite(item['id'])
                    st.toast("Removed from Favorites.")
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.write("No saved responses or quotes yet.")
            
    with tab2:
        st.markdown("### Saved Practices")
        if exercises or plans:
            # Render exercises
            if exercises:
                st.markdown("#### Exercises")
                for item in exercises:
                    st.markdown(f"""
                    <div class="compact-card" style="border-left: 4px solid #6B8E23;">
                        <strong>{item['content'].split(' - ')[0] if ' - ' in item['content'] else 'Exercise'}</strong>
                        <p style="font-size: 14px; color: #555; margin-top: 5px;">
                            {item['content'].split(' - ')[1] if ' - ' in item['content'] else item['content']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Remove", key=f"del_fav_{item['id']}", type="secondary"):
                        db.delete_favorite(item['id'])
                        st.toast("Removed from Favorites.")
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # Render plans
            if plans:
                st.markdown("#### Plans")
                for item in plans:
                    st.markdown(f"""
                    <div class="compact-card" style="border-left: 4px solid #6B8E23;">
                        <strong>{item['content']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Remove", key=f"del_fav_{item['id']}", type="secondary"):
                        db.delete_favorite(item['id'])
                        st.toast("Removed from Favorites.")
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.write("No saved exercises or plans yet.")

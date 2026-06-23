import streamlit as st
import database.db_manager as db
import json
import time

def render_edit_profile(user):
    st.markdown("## 👤 Edit Profile")
    st.markdown("*Keep your personal details updated for personalized wellness guidance.*")
    
    st.markdown('<div class="wellness-card">', unsafe_allow_html=True)
    with st.form("edit_profile_form"):
        name = st.text_input("Full Name", value=user['name'])
        age = st.number_input("Age", min_value=1, max_value=120, value=int(user['age']) if user['age'] else 25)
        occupation = st.text_input("Occupation", value=user['occupation'] if user['occupation'] else "Student")
        
        save_btn = st.form_submit_button("Update Profile 👤")
        
        if save_btn:
            if name.strip():
                db.update_user(user['id'], name.strip(), age, occupation.strip())
                st.success("Profile updated successfully! 🌿")
                st.rerun()
            else:
                st.error("Name cannot be empty.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_export_data(user):
    st.markdown("## 📤 Export Data")
    st.markdown("*Download your entire wellness footprint, logs, and chats.*")
    
    st.markdown('<div class="wellness-card">', unsafe_allow_html=True)
    st.write("We respect your privacy. You can export all your data (profile, history, mood logs, plans, and favorites) stored in this app at any time as a JSON file.")
    
    # Export Data Compilation
    exported_data = db.export_user_data(user['id'])
    
    if exported_data:
        json_str = json.dumps(exported_data, indent=4)
        
        st.download_button(
            label="Download My Data (JSON) 📥",
            data=json_str,
            file_name=f"calmmind_data_{user['name'].lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.error("Failed to compile user data. Please ensure your profile exists.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Delete Profile option (Extra safety and complete data deletion)
    st.markdown("### ⚠️ Danger Zone")
    st.markdown('<div class="compact-card" style="border: 1px solid #ff4b4b;">', unsafe_allow_html=True)
    st.write("Deleting your profile will permanently erase all conversations, mood logs, plans, and favorites. This action is irreversible.")
    
    if st.button("Permanently Delete My Data 🗑️", type="primary"):
        db.delete_user_profile(user['id'])
        st.session_state.clear()
        st.success("Your profile and all data have been completely erased. Returning to landing page...")
        time.sleep(2)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

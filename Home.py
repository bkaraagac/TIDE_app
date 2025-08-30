import streamlit as st

st.set_page_config(page_title="TIDE", layout="centered")

# Create two columns for logo and title
col1, col2 = st.columns([1, 4])  # Adjust width ratio as needed

with col1:
    st.image("C:/Users/karaa/OneDrive - UvA/thesis/TIDE/tide_app/assets", width=100)

with col2:
    st.markdown("## TIDE: Thesis Inspiration Discovery Engine")

st.markdown("""
Welcome to the TIDE tool. This platform helps students explore previous thesis topics 
and get inspiration grounded in real work conducted at their institution.

**Pages:**
- 🗂️ *Upload Theses* 
- ℹ️ *View Extracted Information* 
""")

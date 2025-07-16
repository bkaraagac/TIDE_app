# app.py
import streamlit as st

st.set_page_config(page_title="TIDE", layout="centered")

st.title("📘 TIDE: Thesis Inspiration Discovery Engine")
st.markdown("""
Welcome to the TIDE tool. This platform helps students explore previous thesis topics 
and get inspiration grounded in real work conducted at their institution.

**Pages:**
- 🔼 *Upload Theses* (for thesis coordinators or staff)
- 📊 *View Extracted Topics* (for students to browse and get inspired)
""")

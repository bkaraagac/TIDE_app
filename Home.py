import streamlit as st
from config import ASSETS  # <-- important

st.set_page_config(page_title="TIDE", layout="centered")

# Build the logo path (case-sensitive on Linux/Streamlit Cloud)
logo_path = ASSETS / "image2vector.svg"

# Create two columns for logo and title
col1, col2 = st.columns([1, 4])

with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=120)
    else:
        st.warning("Logo not found at assets/image2vector.svg")

with col2:
    st.markdown("## TIDE: Thesis Inspiration Discovery Engine")


st.markdown("""
Welcome to the TIDE tool. This platform helps students explore previous thesis topics 
and get inspiration grounded in real work conducted at their institution.

**Pages:**
- 🗂️ *Upload Theses* 
- ℹ️ *View Extracted Information* 
""")

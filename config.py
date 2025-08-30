from pathlib import Path
import tempfile
import uuid
import os

# Repo root
ROOT = Path(__file__).resolve().parent

# Folders inside the repo
ASSETS = ROOT / "assets"
DATA   = ROOT / "data"

# Per-session temp dir (works on Streamlit Cloud)
def session_tmp():
    # late import to avoid circular imports during Streamlit bootstrap
    import streamlit as st
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    p = Path(tempfile.gettempdir()) / "tide_app" / st.session_state["session_id"]
    p.mkdir(parents=True, exist_ok=True)
    return p

def output_csv_path():
    return session_tmp() / "extracted_data.csv"

def get_api_key():
    # Prefer secrets on Streamlit Cloud; fall back to env var or manual input
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        key = None
    return key or os.getenv("OPENAI_API_KEY")

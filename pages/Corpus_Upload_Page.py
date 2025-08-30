import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from backend.parser import pdf_to_markdown
from backend.extractor import extract_info, get_client

# Constants
MODEL = "gpt-4o-mini"
FIELDS = [
    "Title",
    "Keywords",
    "Research_Goal",
    "Research_Question",
    "Hypotheses",
    "Methodology",
    "Findings_Summary",
    "Future_Research_Suggestions",
    "Organisation",
    "Author",
    "Supervisor",
    "Study_Programme",
    "Submission_date",
    "Source_File"
]

# Session-based API key storage
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Setup
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("🗂️ Upload Thesis Corpus (ZIP)")
st.caption("💸 *Estimated cost per 100 theses is approximately $0.50 (as of June 2025)*")

# Ask user for OpenAI API key
st.session_state.api_key = st.text_input(
    "🔑 Enter your OpenAI API key", type="password", value=st.session_state.api_key
)

if not st.session_state.api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# Get OpenAI client
client = get_client(st.session_state.api_key)

# Upload ZIP file
uploaded_zip = st.file_uploader("Upload a ZIP file containing thesis PDFs", type="zip")

if uploaded_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "batch.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        pdf_paths = [
            os.path.join(tmpdir, f)
            for f in os.listdir(tmpdir)
            if f.lower().endswith(".pdf")
        ]
        st.info(f"📄 Found {len(pdf_paths)} PDFs.")

        if st.button("Run Extraction Now ▶️"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, path in enumerate(pdf_paths):
                filename = os.path.basename(path)
                status_text.text(f"Processing {filename}...")

                try:
                    thesis_text = pdf_to_markdown(path)
                    result = extract_info(thesis_text, client)

                    # Format hypotheses list if present
                    hyp = result.get("Hypotheses")
                    if isinstance(hyp, list):
                        result["Hypotheses"] = "; ".join(hyp)
                    elif hyp is None:
                        result["Hypotheses"] = "not present"
                    else:
                        result["Hypotheses"] = str(hyp)

                    result["Source_File"] = filename
                    results.append(result)
                    st.success(f"✅ Successfully processed: {filename}")

                except Exception as e:
                    st.error(f"❌ Error processing {filename}: {str(e)}")
                    results.append({
                        **{field: "extraction failed" for field in FIELDS if field != "Source_File"},
                        "Source_File": filename,
                    })

                progress_bar.progress((i + 1) / len(pdf_paths))

            if results:
                df = pd.DataFrame(results)

                for field in FIELDS:
                    if field not in df.columns:
                        df[field] = ""

                df = df[FIELDS]
                df.to_csv("data/extracted_data.csv", index=False)
                st.success(f"✅ Extraction complete. Processed {len(results)} files.")
                st.dataframe(df, use_container_width=True)
            else:
                st.error("No files were successfully processed.")

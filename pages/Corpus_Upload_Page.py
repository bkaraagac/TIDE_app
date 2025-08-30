import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from backend.parser import pdf_to_markdown
from backend.extractor import extract_info, get_client
from config import session_tmp, output_csv_path, get_api_key

# Constants
MODEL = "gpt-4o-mini"
FIELDS = []  # keep as-is if you set column order later

st.title("🗂️ Upload Thesis Corpus (ZIP)")
st.caption("💸 *Estimated cost per 100 theses is approximately $0.50 (as of June 2025)*")

# Get API key (prefer secrets/env; otherwise text input)
api_key = get_api_key()
if not api_key:
    api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
if not api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

client = get_client(api_key)

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
                    # fill missing fields cleanly
                    row = {"Source_File": filename}
                    # if you maintain a list of FIELDS, you can mark failures there
                    for k in result.keys() if results else []:
                        row.setdefault(k, "extraction failed")
                    results.append(row)

                progress_bar.progress((i + 1) / len(pdf_paths))

            if results:
                df = pd.DataFrame(results)

                # Optional: enforce column order if you define FIELDS
                if FIELDS:
                    for field in FIELDS:
                        if field not in df.columns:
                            df[field] = ""
                    df = df[[c for c in FIELDS if c in df.columns]]

                # ✅ Save per-session & keep in memory; DO NOT write to repo
                csv_path = output_csv_path()
                df.to_csv(csv_path, index=False)
                st.session_state["extracted_df"] = df

                st.success(f"✅ Extraction complete. Processed {len(results)} files.")
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    "Download CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "extracted_data.csv",
                    "text/csv",
                )
            else:
                st.error("No files were successfully processed.")

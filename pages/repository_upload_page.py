import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from backend.parser import pdf_to_markdown
from backend.extractor import extract_info
import json

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("📁 Upload Thesis Repository (ZIP)")

uploaded_zip = st.file_uploader("Upload a ZIP file containing thesis PDFs", type="zip")

if uploaded_zip:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save zip to temp
        zip_path = os.path.join(tmpdir, "batch.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        # Extract files
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Filter out PDFs
        pdf_paths = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.lower().endswith(".pdf")]

        st.info(f"📄 Found {len(pdf_paths)} PDFs. Processing...")

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, path in enumerate(pdf_paths):
            filename = os.path.basename(path)
            status_text.text(f"Processing {filename}...")

            try:
                thesis_text = pdf_to_markdown(path)
                result = extract_info(thesis_text)
                result["source_file"] = filename
                results.append(result)

                # Show success for each file
                st.success(f"✅ Successfully processed: {filename}")

            except Exception as e:
                # Handle individual file errors
                st.error(f"❌ Error processing {filename}: {str(e)}")
                # Create a basic error result
                error_result = {
                    "source_file": filename,
                    "error": str(e),
                    "author": "extraction failed",
                    "supervisor": "extraction failed",
                    "study_programme": "extraction failed",
                    "submission_date": "extraction failed",
                    "keywords": "extraction failed",
                    "research_goal": "extraction failed",
                    "research_question": "extraction failed",
                    "hypotheses": "extraction failed",
                    "methodology": "extraction failed",
                    "findings_summary": "extraction failed",
                    "future_research_suggestions": "extraction failed",
                    "organisation": "extraction failed"
                }
                results.append(error_result)

            # Update progress
            progress_bar.progress((i + 1) / len(pdf_paths))

        # Handle hypotheses field conversion for each result
        for result in results:
            hyp = result.get("hypotheses")
            if isinstance(hyp, list):
                result["hypotheses"] = "; ".join(hyp)  # make it a single string
            elif hyp is None:
                result["hypotheses"] = "not present"
            else:
                result["hypotheses"] = str(hyp)

        status_text.text("Processing complete!")

        # Create DataFrame and save to CSV
        if results:
            df = pd.DataFrame(results)
            df.to_csv("data/extracted_data.csv", index=False)

            st.success(f"✅ Extraction complete. Processed {len(results)} files.")
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No files were successfully processed.")


# HIGHLIGHT WHEN PPL WILL BE BILLED & MAKE SURE THEY PUT IN THEIR OWN API, NOT USE MINE
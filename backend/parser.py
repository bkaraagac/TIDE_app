import fitz  # PyMuPDF
import os

def pdf_to_markdown(pdf_path):
    doc = fitz.open(pdf_path)
    markdown_text = ""

    for page in doc:
        blocks = page.get_text("dict")
        for block in blocks["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        text = span["text"]
                        flags = span["flags"]
                        size = span["size"]

                        if flags & 2**4:
                            text = f"**{text}**"
                        if flags & 2**1:
                            text = f"*{text}*"
                        if size > 16:
                            text = f"# {text}"
                        elif size > 14:
                            text = f"## {text}"
                        elif size > 12:
                            text = f"### {text}"

                        line_text += text
                    if line_text.strip():
                        markdown_text += line_text + "\n"
                markdown_text += "\n"
    doc.close()
    return markdown_text

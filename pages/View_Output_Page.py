import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components
import dateparser

DATA_PATH = "data/extracted_data.csv"

# Configure page to be wide and left-aligned
st.set_page_config(page_title="Thesis Inspiration Database", layout="wide")

# Custom CSS for left alignment and full-width table
st.markdown("""
    <style>
    .main .block-container {
        text-align: left;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    h1, h2, h3, h4, h5, h6, p, div {
        text-align: left !important;
    }
    .stTextInput > div > input {
        text-align: left !important;
    }
    .stToggle {
        text-align: left;
    }
    .element-container {
        width: 100% !important;
    }
    .stDataFrame {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("ℹ️ Thesis Inspiration Database")

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)

    # Search input and download button
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search keyword")
    with col2:
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "thesis_data.csv", "text/csv")


    # Filter based on keyword
    if search:
        search_lower = search.lower()
        filtered_df = df[df.apply(lambda row: search_lower in str(row).lower(), axis=1)]

        def highlight_cell(cell):
            if isinstance(cell, str) and search_lower in cell.lower():
                start = cell.lower().index(search_lower)
                end = start + len(search_lower)
                match = cell[start:end]
                return cell[:start] + f"<mark>{match}</mark>" + cell[end:]
            return cell

        display_df = filtered_df.copy()
        for col in display_df.columns:
            display_df[col] = display_df[col].apply(highlight_cell)
        st.write(f"🔍 {len(display_df)} result(s) found:")
    else:
        display_df = df.copy()
        st.write(f"📊 Showing all {len(display_df)} records:")

    expand_table = st.toggle("🔽 Show full table", value=False)
    table_height = 800 if expand_table else 400

    full_html = f"""
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <style>
    .table-wrapper {{
        max-height: {table_height}px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1px solid #ccc;
        width: 100%;
        margin: 0;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        font-size: 14px;
        min-width: max-content;
    }}
    th, td {{
        padding: 8px 12px;
        border: 1px solid #ccc;
        text-align: left;
        white-space: nowrap;
    }}
    td {{
        white-space: normal;
        max-width: 300px;
    }}
    mark {{
        background-color: yellow;
        font-weight: bold;
    }}
    .dataTables_wrapper {{
        width: 100%;
    }}
    .dataTables_scrollHead, .dataTables_scrollBody {{
        width: 100% !important;
    }}
    </style>

    <div class="table-wrapper">
        {display_df.to_html(index=False, escape=False, table_id="sortable-table")}
    </div>

    <script>
        const waitForJQuery = () => {{
            if (window.jQuery) {{
                $('#sortable-table').DataTable({{
                    paging: false,
                    info: false,
                    searching: false,
                    scrollX: true,
                    autoWidth: false,
                    columnDefs: [{{ targets: '_all', className: 'dt-left' }}]
                }});
            }} else {{
                setTimeout(waitForJQuery, 100);
            }}
        }};
        waitForJQuery();
    </script>
    """

    components.html(full_html, height=table_height + 100, scrolling=True)

else:
    st.warning("No extracted thesis data found. Please upload PDFs first.")

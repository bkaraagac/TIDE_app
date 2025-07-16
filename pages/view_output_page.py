import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

DATA_PATH = "data/extracted_data.csv"

# Configure page to be wide and left-aligned
st.set_page_config(page_title="Thesis Inspiration Database", layout="wide")

# Custom CSS for left alignment and full-width table
st.markdown("""
    <style>
    /* Left align the entire page */
    .main .block-container {
        text-align: left;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    /* Left align all text elements */
    h1, h2, h3, h4, h5, h6, p, div {
        text-align: left !important;
    }

    /* Left align input fields */
    .stTextInput > div > input {
        text-align: left !important;
    }

    /* Left align toggle */
    .stToggle {
        text-align: left;
    }

    /* Remove default streamlit margins for full width */
    .element-container {
        width: 100% !important;
    }

    /* Make dataframe full width */
    .stDataFrame {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📘 Thesis Inspiration Database")

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    st.dataframe(df, use_container_width=True)  # Optional preview at the top

    search = st.text_input("Search keyword")
    if search:
        search_lower = search.lower()

        # Filter rows that contain the search keyword in any cell
        filtered = df[df.apply(lambda row: search_lower in str(row).lower(), axis=1)]
        st.write(f"🔍 {len(filtered)} result(s) found:")


        def highlight_cell(cell):
            if isinstance(cell, str) and search_lower in cell.lower():
                start = cell.lower().index(search_lower)
                end = start + len(search_lower)
                match = cell[start:end]
                return cell[:start] + f"<mark>{match}</mark>" + cell[end:]
            return cell


        # Highlight the matches
        highlighted_df = filtered.copy()
        for col in highlighted_df.columns:
            highlighted_df[col] = highlighted_df[col].apply(highlight_cell)

        # Toggle for full-height display
        expand_table = st.toggle("🔽 Show full table", value=False)

        # Set height based on toggle
        table_height = 800 if expand_table else 400

        # Full HTML output for DataTables + highlight styling
        full_html = f"""
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

        <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: sans-serif;
        }}

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
            min-width: max-content; /* This ensures table is as wide as needed */
        }}

        th, td {{
            padding: 8px 12px;
            border: 1px solid #ccc;
            text-align: left;
            white-space: nowrap; /* Prevents text wrapping, making columns wider */
        }}

        /* Allow text wrapping in cells if needed, remove this if you want nowrap */
        td {{
            white-space: normal;
            max-width: 300px; /* Adjust as needed */
        }}

        mark {{
            background-color: yellow;
            font-weight: bold;
        }}

        /* DataTables styling adjustments */
        .dataTables_wrapper {{
            width: 100%;
        }}

        .dataTables_scrollHead,
        .dataTables_scrollBody {{
            width: 100% !important;
        }}
        </style>

        <div class="table-wrapper">
            {highlighted_df.to_html(index=False, escape=False, table_id="sortable-table")}
        </div>

        <script>
            const waitForJQuery = () => {{
                if (window.jQuery) {{
                    $('#sortable-table').DataTable({{
                        paging: false,
                        info: false,
                        searching: false,
                        scrollX: true, /* Enable horizontal scrolling */
                        autoWidth: false, /* Let columns size naturally */
                        columnDefs: [
                            {{ targets: '_all', className: 'dt-left' }} /* Left align all columns */
                        ]
                    }});
                }} else {{
                    setTimeout(waitForJQuery, 100);
                }}
            }};
            waitForJQuery();
        </script>
        """

        # Render as component with scrolling enabled
        components.html(full_html, height=table_height + 100, scrolling=True)

else:
    st.warning("No extracted thesis data found. Please upload PDFs first.")
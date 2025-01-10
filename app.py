import streamlit as st
import logging
from core.session_state import initialize_session_state
from core.layout import render_main_header, layout_main_columns
from core.sidebar import display_sidebar

# ---------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger()

# ---------------------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="✨ Causal DAG Summarization Tool",
    layout="wide"
)

# ---------------------------------------------------------------------
# Main App Logic
# ---------------------------------------------------------------------

def main():
    initialize_session_state()
    render_main_header()
    display_sidebar()
    layout_main_columns()

if __name__ == "__main__":
    main()

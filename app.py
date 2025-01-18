import streamlit as st
import logging
from core.session_state import initialize_session_state
from core.layout import render_main_header, layout_main_columns
from core.sidebar import display_sidebar
from random import seed
import os
import asyncio
seed(None)

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
    page_title="🔀 Causal DAG Summarization Tool",
    layout="wide"
)

# Cross platform compatability
logo_path = os.path.abspath("dag_logo.png")

# ---------------------------------------------------------------------
# Main App Logic
# ---------------------------------------------------------------------

async def main():
    initialize_session_state()
    render_main_header(logo_path=logo_path, title_text="Causal DAG Summarization Tool")
    await display_sidebar()
    layout_main_columns()

if __name__ == "__main__":
    asyncio.run(main())

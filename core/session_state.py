import streamlit as st
import pandas as pd

def initialize_session_state():
    if "original_dag" not in st.session_state:
        st.session_state.original_dag = None
    if "summarized_dag" not in st.session_state:
        st.session_state.summarized_dag = None
    if "dataset" not in st.session_state:
        st.session_state.dataset = None
    if "size_constraint" not in st.session_state:
        st.session_state.size_constraint = 5
    if "semantic_threshold" not in st.session_state:
        st.session_state.semantic_threshold = 0.5
    if "df" not in st.session_state:
        st.session_state.df = None

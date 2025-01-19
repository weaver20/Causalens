import streamlit as st
import os
from utils.lottie_loader import get_animation_data

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
    if "generate_button" not in st.session_state:
        st.session_state.generate_button = False
    if "loaded_dot" not in st.session_state:
        st.session_state.loaded_dot = False
    if "dag_file" not in st.session_state:
        st.session_state.dag_file = None
    if "generation_type" not in st.session_state:
        st.session_state.generation_type = None
    if "loading_animation" not in st.session_state:
        animation_path = os.path.abspath("loading_animation.json")
        st.session_state.loading_animation = get_animation_data(animation_path)
    if "summarize_button" not in st.session_state:
        st.session_state.summarize_button = False

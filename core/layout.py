import streamlit as st
import time
from streamlit_lottie import st_lottie_spinner
from dag_display.display_dag import display_dag_column
from utils.graph_utils import (load_dag_from_file,
                               generate_dag_from_dataset,
                               summarize_dag)

def render_main_header(logo_path: str, title_text: str):
    col1, col2 = st.columns([1, 7])  # Adjust ratio as desired
    with col1:
        st.image(logo_path, use_container_width="auto")  # Set an appropriate width
    with col2:
        st.markdown(f"""
    <h1 style="
        margin-top: 0px;
        margin-bottom: 20px;
        font-family: 'Helvetica', sans-serif;
        font-size: 48px;
        font-weight: bold;
        background: linear-gradient(to right, #16BFFD, #CB3066);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
        letter-spacing: 1px;
    ">
        {title_text}
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("""
    ### Summarize a Causal DAG using the CaGreS Algorithm

    * **Upload** a `.dot` file or **generate** a sample DAG.
    * **Configure** size constraint & semantic threshold in the sidebar.
    * **Visualize** the DAG with color-coded nodes.
    * **Add / Remove edges** safely.
    * **Summarize** with CaGreS, then compute causal effect.
    """)

def layout_main_columns():
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.session_state.generate_button:
            with st_lottie_spinner(st.session_state.loading_animation, height=500, quality='high'):
                if st.session_state.generation_type == "dataset":
                    st.session_state.original_dag = generate_dag_from_dataset(st.session_state.df, alpha=st.session_state.alpha)
                else:
                    time.sleep(4)
                    st.session_state.original_dag = load_dag_from_file(st.session_state.dag_file)
                st.toast("Generated Causal DAG successfully!")
                st.session_state.generate_button = False
                st.rerun()
        else:
            display_dag_column("Original Causal DAG", st.session_state.original_dag, is_original=True)

    with c2:
        if st.session_state.summarize_button:
            with st_lottie_spinner(st.session_state.loading_animation, height=500, quality='high'):
                st.session_state.summarized_dag = summarize_dag()
                if st.session_state.summarized_dag:
                    st.toast("Summarized DAG successfully!")
                    st.session_state.summarize_button = False
                    time.sleep(2)
                    st.rerun()
            st.warning("Could not summarize DAG with given constraints!")
        else:
            display_dag_column("Summarized Causal DAG", st.session_state.summarized_dag, is_original=False)

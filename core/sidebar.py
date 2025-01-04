import streamlit as st
from utils.graph_utils import (
    load_dag_from_file,
    generate_dag_algorithm,
    generate_dag_from_dataset,
)

def display_sidebar():
    with st.sidebar.expander("1. Upload or Generate DAG", expanded=True):
        sidebar_upload_or_generate_dag()

    with st.sidebar.expander("2. Configuration Parameters"):
        sidebar_configuration()

    with st.sidebar.expander("Compute Causal Effects"):
        sidebar_compute_causal_effects()


def sidebar_upload_or_generate_dag():
    dag_file = st.file_uploader("Upload Causal DAG (.dot)", type=["dot"])
    data_file = st.file_uploader("Upload Dataset File (optional):")

    c1, c2 = st.columns([1, 1])
    with c1:
        gen_btn = st.button("Generate DAG")
    with c2:
        reset_btn = st.button("Reset DAG")

    if reset_btn:
        st.session_state.original_dag = None
        st.session_state.summarized_dag = None
        st.info("DAG has been reset.")
        st.experimental_rerun()

    if st.session_state.original_dag is None:
        if dag_file:
            loaded_dag = load_dag_from_file(dag_file)
            if loaded_dag:
                st.session_state.original_dag = loaded_dag
                st.success("DAG uploaded successfully!")
        elif data_file and gen_btn:
            st.session_state.dataset = data_file.getvalue()
            new_dag = generate_dag_from_dataset(st.session_state.dataset)
            st.session_state.original_dag = new_dag
            st.success("DAG generated from dataset.")
        elif gen_btn and data_file is None:
            st.session_state.original_dag = generate_dag_algorithm()
            st.success("Placeholder DAG generated.")
    else:
        st.info("A DAG is already loaded. Click 'Reset DAG' to start fresh.")


def sidebar_configuration():
    if st.session_state.original_dag:
        st.session_state.size_constraint = st.number_input(
            "Size Constraint:", min_value=1, value=5, max_value=50
        )
        st.session_state.semantic_threshold = st.slider(
            "Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05
        )
    else:
        st.info("Please upload/generate a DAG to configure summarization.")


def sidebar_compute_causal_effects():
    if st.session_state.original_dag is None:
        st.error("No original DAG for computing ATE.")
        return

    graph_options = ["Original DAG"]
    if st.session_state.summarized_dag is not None:
        graph_options.append("Summarized DAG")

    chosen = st.selectbox("Select Graph:", graph_options, index=0)
    if chosen == "Original DAG":
        g = st.session_state.original_dag
    else:
        g = st.session_state.summarized_dag

    nodes_list = list(g.nodes())
    treatment = st.selectbox("Select Treatment:", nodes_list)
    outcome = st.selectbox("Select Outcome:", nodes_list)

    if st.button("Compute ATE"):
        st.write(f"Computing ATE...")
        st.success("ATE computation has not been implemented yet.")

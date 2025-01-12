import streamlit as st
import Utils
from algorithms import algo
from utils.graph_utils import (
    load_dag_from_file,
    generate_dag_algorithm,
)

TOKEN_PATTERN = r"""
        (?P<LPAREN>\() |
        (?P<RPAREN>\)) |
        (?P<NOT>NOT\b) |
        (?P<AND>AND\b) |
        (?P<OR>OR\b) |
        (?P<COND>(?P<NODE>[A-Za-z0-9_]+)\s*(?P<OP>==|!=|<=|>=|<|>)\s*(?P<VAL>("[^"]*"|'[^']*'|[A-Za-z0-9_.]+)))
    """

def display_sidebar():
    with st.sidebar.expander("1. Upload or Generate DAG", expanded=True):
        sidebar_upload_or_generate_dag()

    with st.sidebar.expander("2. Configuration Parameters"):
        sidebar_configuration()

    with st.sidebar.expander("Compute Causal Effects"):
        sidebar_compute_causal_effects()


def sidebar_upload_or_generate_dag():
    dag_file = st.file_uploader("Upload Causal DAG (.dot)", type=["dot"])

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
        elif gen_btn:
            st.session_state.original_dag = generate_dag_algorithm()
            st.success("Placeholder DAG generated.")
    else:
        st.info("A DAG is already loaded. Click 'Reset DAG' to start fresh.")


def sidebar_configuration():
    def reset_summary_dag():
        st.session_state.summarized_dag = None

    if st.session_state.original_dag:
        st.session_state.size_constraint = st.number_input(
            "Size Constraint:", min_value=1, value=5, max_value=50, on_change=reset_summary_dag
        )
        st.session_state.semantic_threshold = st.slider(
            "Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05, on_change=reset_summary_dag
        )
    else:
        st.info("Please upload/generate a DAG to configure summarization.")


def sidebar_compute_causal_effects():
    if st.session_state.original_dag is None:
        st.error("No original DAG for computing ATE.")
        return
    
    # 1) Upload a dataset
    dataset = st.file_uploader("Upload Dataset File (optional):", type=["pkl"])
    if dataset is None:
        st.error("No dataset uploaded for computing the ATE.")
        return
    
    # 2) Graph Selection
    graph_options = ["Original DAG"]
    if st.session_state.summarized_dag is not None:
        graph_options.append("Summarized DAG")

    chosen_graph_label = st.selectbox("Select Graph:", graph_options, index=0)

    if chosen_graph_label == "Original DAG":
        G = st.session_state.original_dag
    else:
        summary_dag = st.session_state.summarized_dag
        G = algo.get_grounded_dag(summary_dag)
    G = Utils.convert_nodes_snake_to_pascal_case(G)

    # 3) Treatment
    nodes_list = list(st.session_state.original_dag.nodes())
    treatment_node = st.selectbox("Select Treatment Node:", nodes_list)

    condition_input = st.text_input(
        "Enter logic condition for the Treatment Node:",
        value="",
        placeholder="e.g. NumColumns == 4 or NumColumns <= 5"
    )

    # 4) Outcome Selection
    outcome_node = st.selectbox("Select Outcome:", nodes_list)

    # 5) Compute Button
    if st.button("Compute ATE"):
        condition_res = Utils.is_valid_condition(condition_input, treatment_node)
        if not condition_res[0]:
            st.error(
                "Invalid logic condition. " + condition_res[1]
            )
        else:
            estimate_res = algo.estimate_binary_treatment_effect(
                    dataset, 
                    treatment_node, 
                    condition_input, 
                    outcome_node, 
                    G)
            st.success(f"Mean Value: {estimate_res[0]}")
            st.success(f"P Value: {estimate_res[1]}")
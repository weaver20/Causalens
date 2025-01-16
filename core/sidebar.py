import streamlit as st
import pandas as pd
from asyncio import (create_task,
                     InvalidStateError)
import time
import logging
import Utils
from algorithms import algo
from utils.graph_utils import load_dag_from_file

logger = logging.getLogger(__name__)

TOKEN_PATTERN = r"""
        (?P<LPAREN>\() |
        (?P<RPAREN>\)) |
        (?P<NOT>NOT\b) |
        (?P<AND>AND\b) |
        (?P<OR>OR\b) |
        (?P<COND>(?P<NODE>[A-Za-z0-9_]+)\s*(?P<OP>==|!=|<=|>=|<|>)\s*(?P<VAL>("[^"]*"|'[^']*'|[A-Za-z0-9_.]+)))
    """

async def display_sidebar():
    with st.sidebar.expander("1. Upload or Generate DAG", expanded=True):
        sidebar_upload_or_generate_dag()

    with st.sidebar.expander("2. Configuration Parameters"):
        sidebar_configuration()

    with st.sidebar.expander("Compute Causal Effects"):
        await sidebar_compute_causal_effects()


def sidebar_upload_or_generate_dag():
    dag_file = st.file_uploader("Upload Causal DAG:", type=["dot"])
    pkl_file  = st.file_uploader("Upload Dataset:", type=["pkl"])
    
    c1, c2 = st.columns([1, 1])
    with c1:
        gen_btn = st.button("Generate DAG", help="Generates the DAG represented by the uploaded dataset")
    with c2:
        refresh_btn = st.button("Refresh")

    if refresh_btn:
        st.session_state.original_dag = None
        st.session_state.summarized_dag = None
        st.session_state.df = None
        st.info("DAG has been reset.")
        st.experimental_rerun()

    if st.session_state.original_dag is None:
        if dag_file:
            loaded_dag = load_dag_from_file(dag_file)
            if loaded_dag:
                st.session_state.original_dag = loaded_dag
                st.toast("DAG uploaded successfully!", icon='😍')

        elif gen_btn:
            #st.session_state.original_dag = generate_dag_algorithm()
            st.warning("Generating DAG from a dataset has not yet been implemented")

    if pkl_file:
        try:
            st.session_state.df = pd.read_pickle(pkl_file)
            st.toast("Dataset uploaded successfully!", icon='😍')
        except Exception as e:
            st.error(f"Please upload a valid .pkl file for dataset!: {e}")
            logger.exception("Exception occurred while loading DOT file: %s", e)
            return

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


async def sidebar_compute_causal_effects():
    # 1) Check DAG and dataframe are present
    if st.session_state.original_dag is None:
        st.info("No original DAG for computing ATE.")
        return
    
    if st.session_state.df is None:
        st.info("No dataset uploaded for computing the ATE.")
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
    nodes_list = list(G.nodes)
    treatment_node = st.selectbox("Select Treatment Node:", nodes_list)

    condition_input = st.text_input(
        "Enter logic condition for the Treatment Node:",
        value="",
        placeholder="e.g. NumColumns == 4 or NumColumns <= 5"
    )

    # 4) Outcome Selection
    outcome_node = st.selectbox("Select Outcome:", nodes_list)

    # 5) Compute Button
    if st.button(":gray[$Compute ATE$]", type='primary'):
        condition_res = Utils.is_valid_condition(condition_input, treatment_node)[0]
        if not condition_res:
            st.error(
                "Invalid logic condition. " + str(condition_res)
            )
        else:
            progress_text = "Calculating ATE. Please wait..."
            with st.spinner(progress_text): 
                df = st.session_state.df
                estimate_res = await algo.estimate_binary_treatment_effect(df, 
                        treatment_node, 
                        condition_input, 
                        outcome_node, 
                        G)
                
                time.sleep(1)
                if estimate_res == (-1, -1):
                    st.error(f"There is no direct path between {treatment_node} to {outcome_node}")
                    return
                
                mean_val = str(estimate_res[1])
                stat_significance = "YES" if estimate_res[1] < 0.05 else "NO"
                
                st.success(f"Mean Value: {mean_val}")
                st.success(f"Statistic Significance: {stat_significance}")
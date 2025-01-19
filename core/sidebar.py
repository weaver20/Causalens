import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import logging
import Utils
from algorithms import algo

logger = logging.getLogger(__name__)

TOKEN_PATTERN = r"""
        (?P<LPAREN>\() |
        (?P<RPAREN>\)) |
        (?P<NOT>NOT\b) |
        (?P<AND>AND\b) |
        (?P<OR>OR\b) |
        (?P<COND>(?P<NODE>[A-Za-z0-9_]+)\s*(?P<OP>==|!=|<=|>=|<|>)\s*(?P<VAL>("[^"]*"|'[^']*'|[A-Za-z0-9_.]+)))
    """

ALPHA_USAGE = "Significance level for PC discovery algorithm $s.t\ \\boldsymbol{\\alpha} \\propto \\textbf{|E|}$"
SIZE_USAGE  = "Set a size constarint $S\ s.t\quad |V_s| \leq S$ where $G_s \equiv (V_s,E_s)$"
SIMILARITY_USAGE = "Set a threshold $s.t\quad  \\forall u,v \\in G\quad u,v \\in G_s \\iff sim(u,v) \geq threshold$ "
GEN_USAGE = "Generates the DAG represented by the uploaded dataset"

async def display_sidebar():
    with st.sidebar:
        # Create the option menu
        selected = option_menu(
            "Main Menu",
            ["1. Upload/Generate DAG", "2. Configuration", "3. Compute Causal Effect"],
            icons=["cloud-upload", "gear", "calculator"],
            menu_icon="cast",
            default_index=0
        )

        # Conditionally show expanders below the menu
        if selected == "1. Upload/Generate DAG":
            with st.expander("Upload or Generate DAG", expanded=True):
                sidebar_upload_or_generate_dag()

        if selected == "2. Configuration":
            with st.expander("Configuration Parameters", expanded=True):
                sidebar_configuration()
        if selected == "3. Compute Causal Effect":
            with st.expander("Compute Causal Effect", expanded=True):
                await sidebar_compute_causal_effects()

def reset_summary_dag():
        st.session_state.summarized_dag = None

def sidebar_upload_or_generate_dag():
    # 1) Handling DAG input
    st.session_state.dag_file = st.file_uploader("Upload Causal DAG:", type=["dot"])
    
    # 2) Handling dataset input
    dataset_pkl_file  = st.file_uploader("Upload Dataset:", type=["pkl"])
    if dataset_pkl_file:
        try:
            st.session_state.df = pd.read_pickle(dataset_pkl_file)
            st.toast("Dataset uploaded successfully!", icon='😍')
        except Exception as e:
            st.session_state.df = None
            st.error(f"Please upload a valid .pkl file for dataset!: {e}")
            logger.exception("Exception occurred while loading DOT file: %s", e)
            return
        
    # 3) Buttons
    c1, c2 = st.columns([1, 1])
    with c1:
        st.session_state.generation_type = st.radio(
            "Genrate DAG From:",
            ["dataset", ".dot file"],
            horizontal=True,
            help="Choose which input should be used for DAG generation"
        )

        if st.button("Refresh"):
            st.session_state.original_dag = None
            st.session_state.summarized_dag = None
            st.session_state.df = None
            st.session_state.dag_file = None
            st.toast("DAG has been reset.")
            time.sleep(0.7)
            st.rerun()
        

    with c2:
        gen_btn = st.button("Generate DAG", help=GEN_USAGE)
        st.session_state.alpha = st.slider("$\\alpha$:", min_value=0.01, value=0.5, max_value=0.99, step=0.01,
                                            on_change=reset_summary_dag, help=ALPHA_USAGE) 
        if gen_btn:
            if st.session_state.generation_type == "dataset" and st.session_state.df is None:
                st.toast("Please upload a .PKL dataset before choosing this option.")
                return
            elif st.session_state.generation_type == ".dot file" and st.session_state.dag_file is None:
                st.toast("Please upload a .DOT file before choosing this option.")
                return
            else:
                st.session_state.generate_button = True
                st.rerun()


def sidebar_configuration():
    if st.session_state.original_dag:
        st.session_state.size_constraint = st.number_input(
            "Size Constraint:", min_value=1, value=5, max_value=50, on_change=reset_summary_dag, help=SIZE_USAGE
        )
        st.session_state.semantic_threshold = st.slider(
            "Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05, on_change=reset_summary_dag, help=SIMILARITY_USAGE
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
import streamlit as st
import networkx as nx
import logging

# Local imports
from graph_utils import (
    load_dag_from_file,
    generate_dag_algorithm,
    generate_dag_from_dataset,
    is_valid_dag,
)
from summarization import summarize_dag
from visualization import visualize_dag_with_plotly

# Configure logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger()

logger.info("Starting Causal DAG Summarization Tool")

st.set_page_config(page_title="Causal DAG Summarization Tool", layout="wide")

# -----------------------------
# Initialize session state
# -----------------------------
if "original_dag" not in st.session_state:
    st.session_state.original_dag = None
if "summarized_dag" not in st.session_state:
    st.session_state.summarized_dag = None
if "dataset" not in st.session_state:
    st.session_state.dataset = None

# For stable layout in the original/summarized graphs
if "original_positions" not in st.session_state:
    st.session_state.original_positions = None
if "summarized_positions" not in st.session_state:
    st.session_state.summarized_positions = None

st.title("Causal DAG Summarization Tool")
st.markdown("### A UI for Summarizing and Interacting with Causal DAGs")

# -----------------------------
# 1. Upload / Generate DAG
# -----------------------------
with st.sidebar.expander("1. Upload or Generate DAG"):
    dag_file = st.file_uploader("Upload Causal DAG File (.dot)", type=["dot"])
    
    data_file = st.file_uploader("Upload Dataset File (optional):")

    col_btns = st.columns([1,1])
    with col_btns[0]:
        generate_btn = st.button("Generate DAG")
    with col_btns[1]:
        reset_dag_btn = st.button("Reset DAG")

    # 1A) Reset logic: if user wants to start fresh
    if reset_dag_btn:
        st.session_state.original_dag = None
        st.session_state.original_positions = None
        st.info("DAG has been reset. Now you can upload or generate again.")
        st.experimental_rerun()

    # 1B) Load/Generate the DAG only if we don't have one in memory
    if st.session_state.original_dag is None:

        # (a) If a .dot file is uploaded, load it
        if dag_file is not None:
            logger.info("DAG file uploaded by user.")
            loaded_dag = load_dag_from_file(dag_file)
            if loaded_dag:
                st.session_state.original_dag = loaded_dag
                st.session_state.original_positions = None
                st.success("DAG uploaded and loaded successfully!")
            else:
                st.error("Failed to load DAG from the .dot file.")

        # (b) Or if we have a dataset and the user clicks "Generate DAG" from dataset
        elif data_file is not None and generate_btn:
            st.session_state.dataset = data_file.getvalue()
            st.success("Dataset uploaded successfully! Generating DAG from dataset...")
            dag_from_data = generate_dag_from_dataset(st.session_state.dataset)
            st.session_state.original_dag = dag_from_data
            st.session_state.original_positions = None
            logger.info("DAG generated from dataset successfully.")

        # (c) Or if the user wants to generate a placeholder DAG (no data_file)
        elif generate_btn and data_file is None:
            st.session_state.original_dag = generate_dag_algorithm()
            st.session_state.original_positions = None
            st.success("Placeholder DAG generated successfully!")
            logger.info("Placeholder DAG generated.")
    
    else:
        # We already have an original DAG in memory
        st.info("A DAG is already loaded in memory. Click 'Reset DAG' to load or generate a new one.")

    # Show nodes/edges if we have a DAG now
    if st.session_state.original_dag:
        st.write("### Current Original DAG (Nodes):", list(st.session_state.original_dag.nodes))
        st.write("### Current Original DAG (Edges):", list(st.session_state.original_dag.edges))

# -----------------------------
# 2. Configuration
# -----------------------------
with st.sidebar.expander("2. Configuration Parameters"):
    size_constraint = st.number_input("Size Constraint:", min_value=1, value=10)
    semantic_threshold = st.slider("Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05)

# -----------------------------
# 3. Summarize DAG
# -----------------------------
@st.cache_data
def cached_summarize_dag(original_dag, size_constraint, semantic_threshold):
    logger.debug(f"Caching summarize_dag with size_constraint={size_constraint}, semantic_threshold={semantic_threshold}")
    return summarize_dag(original_dag, size_constraint, semantic_threshold)

with st.sidebar.expander("3. Summarize DAG"):
    summarize_button = st.button("Summarize Data")
    if summarize_button:
        if st.session_state.original_dag is None:
            st.sidebar.warning("Please provide or generate a DAG before summarizing.")
            logger.warning("Summarization attempted without a DAG.")
        else:
            with st.spinner("Summarizing DAG..."):
                try:
                    st.session_state.summarized_dag = cached_summarize_dag(
                        st.session_state.original_dag, size_constraint, semantic_threshold
                    )
                    st.sidebar.success("DAG summarized successfully!")
                    logger.info("DAG summarized successfully.")
                    
                    # Reset positions so new summarization triggers new layout
                    st.session_state.summarized_positions = None

                    # Display summarized DAG nodes and edges
                    st.write("### Summarized DAG Nodes:", list(st.session_state.summarized_dag.nodes))
                    st.write("### Summarized DAG Edges:", list(st.session_state.summarized_dag.edges))
                except Exception as e:
                    st.sidebar.error("Failed to summarize DAG.")
                    logger.exception(f"Error during DAG summarization: {e}")

# -----------------------------
# 4. Edit Original Graph
# -----------------------------
with st.sidebar.expander("4. Edit Original Graph"):
    if st.session_state.original_dag is not None:
        add_edge_nodes = st.text_input(
            "Add edge (format: Node1,Node2):",
            value="",
            help="Enter the nodes separated by a comma. Example: A,B"
        )
        remove_edge_nodes = st.text_input(
            "Remove edge (format: Node1,Node2):",
            value="",
            help="Enter the nodes separated by a comma. Example: A,B"
        )
        apply_edits = st.button("Apply Edits to Original DAG")
        if apply_edits:
            # Edge addition
            if add_edge_nodes.strip():
                try:
                    n1, n2 = [x.strip() for x in add_edge_nodes.split(",")]
                    st.session_state.original_dag.add_edge(n1, n2)
                    st.success(f"Edge ({n1} → {n2}) added to the original DAG.")
                    logger.info(f"Edge ({n1} → {n2}) added to original DAG.")
                except ValueError as ve:
                    st.error("Invalid format for adding edge. Use 'Node1,Node2'.")
                    logger.warning(f"Invalid format for adding edge: {ve}")
                except Exception as e:
                    st.error(f"Error adding edge: {e}")
                    logger.exception(f"Error adding edge: {e}")

            # Edge removal
            if remove_edge_nodes.strip():
                try:
                    n1, n2 = [x.strip() for x in remove_edge_nodes.split(",")]
                    if st.session_state.original_dag.has_edge(n1, n2):
                        st.session_state.original_dag.remove_edge(n1, n2)
                        st.success(f"Edge ({n1} → {n2}) removed from the original DAG.")
                        logger.info(f"Edge ({n1} → {n2}) removed from original DAG.")
                    else:
                        st.warning("That edge does not exist.")
                        logger.warning(f"Attempted to remove non-existent edge ({n1} → {n2}).")
                except ValueError as ve:
                    st.error("Invalid format for removing edge. Use 'Node1,Node2'.")
                    logger.warning(f"Invalid format for removing edge: {ve}")
                except Exception as e:
                    st.error(f"Error removing edge: {e}")
                    logger.exception(f"Error removing edge: {e}")

            # If you want to recalculate positions after every edit, uncomment:
            # st.session_state.original_positions = None

            st.experimental_rerun()
    else:
        st.warning("No original DAG is loaded. Please upload or generate one first.")

# -----------------------------
# 5. Compute Causal Effects (placeholder)
# -----------------------------
with st.sidebar.expander("5. Compute Causal Effects"):
    if st.session_state.original_dag is not None:
        all_nodes = list(st.session_state.original_dag.nodes)
        if len(all_nodes) < 2:
            st.warning("Need at least two nodes to compute causal effects.")
            logger.warning("Causal effect computation attempted with <2 nodes.")
        else:
            node1 = st.selectbox("Select Node 1:", all_nodes, key="node1")
            node2 = st.selectbox("Select Node 2:", all_nodes, key="node2")
            graph_choice = st.selectbox("Apply computation to:", ["Original Graph", "Summarized Graph"], key="graph_choice")
            compute_effect = st.button("Compute Causal Effect")
            if compute_effect:
                chosen_graph = st.session_state.original_dag if graph_choice == "Original Graph" else st.session_state.summarized_dag
                if chosen_graph is not None:
                    # Placeholder for actual causal effect computation
                    effect = 0.5
                    st.write(f"Causal effect of {node1} on {node2} in {graph_choice}: {effect} (placeholder)")
                    logger.info(f"Causal effect computed for {node1} on {node2} in {graph_choice}: {effect}")
                else:
                    st.error("Selected graph is not available.")
                    logger.error("Selected graph for causal effect computation is not available.")
    else:
        st.warning("No original DAG is loaded. Please upload or generate one first.")

# -------------------------------------------
# Main Page Visualizations
# -------------------------------------------
col1, col2 = st.columns(2)

# ---------- Original Graph ----------
col1.subheader("Original Causal DAG")
if st.session_state.original_dag is not None:
    if is_valid_dag(st.session_state.original_dag):
        if st.session_state.original_positions is None:
            st.session_state.original_positions = nx.spring_layout(st.session_state.original_dag, seed=42)
        fig_original = visualize_dag_with_plotly(
            st.session_state.original_dag, 
            positions=st.session_state.original_positions
        )
        if fig_original:
            col1.plotly_chart(fig_original, use_container_width=True)
        else:
            col1.error("Failed to generate Plotly figure for the original DAG.")
    else:
        col1.warning("The original graph is not a valid Directed Acyclic Graph (DAG).")
else:
    col1.write("No original DAG available.")

# ---------- Summarized Graph ----------
col2.subheader("Summarized Graph")
if st.session_state.summarized_dag is not None:
    if is_valid_dag(st.session_state.summarized_dag):
        if st.session_state.summarized_positions is None:
            st.session_state.summarized_positions = nx.spring_layout(st.session_state.summarized_dag, seed=42)
        fig_summarized = visualize_dag_with_plotly(
            st.session_state.summarized_dag,
            positions=st.session_state.summarized_positions
        )
        if fig_summarized:
            col2.plotly_chart(fig_summarized, use_container_width=True)
        else:
            col2.error("Failed to generate Plotly figure for the summarized DAG.")
    else:
        col2.warning("The summarized graph is not a valid Directed Acyclic Graph (DAG).")
else:
    col2.write("No summarized DAG available yet.")

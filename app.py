import streamlit as st
import networkx as nx
import logging
import streamlit.components.v1 as components

# Local imports
from graph_utils import (
    load_dag_from_file,
    generate_dag_algorithm,
    generate_dag_from_dataset,
    is_valid_dag,
)
from summarization import summarize_dag
from visualization import visualize_dag_with_pyvis

# Configure logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger()

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

st.title("Causal DAG Summarization Tool")
st.markdown("### A UI for Summarizing and Interacting with Causal DAGs")

# -----------------------------
# 1. Sidebar: Upload / Generate
# -----------------------------
with st.sidebar.expander("1. Upload or Generate DAG"):
    dag_file = st.file_uploader("Upload Causal DAG File (.dot)", type=["dot"])
    data_file = st.file_uploader("Upload Dataset File (optional):")

    col_btns = st.columns([1,1])
    with col_btns[0]:
        generate_btn = st.button("Generate DAG")
    with col_btns[1]:
        reset_btn = st.button("Reset DAG")

    if reset_btn:
        st.session_state.original_dag = None
        st.session_state.summarized_dag = None
        st.info("DAG has been reset.")
        st.experimental_rerun()

    if st.session_state.original_dag is None:
        # If no DAG in memory, see if user uploaded or wants to generate
        if dag_file is not None:
            loaded_dag = load_dag_from_file(dag_file)
            if loaded_dag:
                st.session_state.original_dag = loaded_dag
                st.success("DAG uploaded successfully!")
        elif data_file is not None and generate_btn:
            st.session_state.dataset = data_file.getvalue()
            new_dag = generate_dag_from_dataset(st.session_state.dataset)
            st.session_state.original_dag = new_dag
            st.success("DAG generated from dataset.")
        elif generate_btn and data_file is None:
            st.session_state.original_dag = generate_dag_algorithm()
            st.success("Placeholder DAG generated.")
    else:
        st.info("A DAG is already loaded. Reset if you want a fresh one.")

    if st.session_state.original_dag:
        st.write("**Original DAG Nodes:**", list(st.session_state.original_dag.nodes))
        st.write("**Original DAG Edges:**", list(st.session_state.original_dag.edges))

# -----------------------------
# 2. Sidebar: Configuration
# -----------------------------
with st.sidebar.expander("2. Configuration Parameters"):
    size_constraint = st.number_input("Size Constraint:", min_value=1, value=10)
    semantic_threshold = st.slider("Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05)

# Summarization with caching
@st.cache_data
def cached_summarize_dag(original_dag, size_cons, sem_thresh):
    return summarize_dag(original_dag, size_cons, sem_thresh)

# -----------------------------
# 3. Sidebar: Summarize DAG
# -----------------------------
with st.sidebar.expander("3. Summarize DAG"):
    summ_btn = st.button("Summarize Data")
    if summ_btn:
        if st.session_state.original_dag is None:
            st.warning("No DAG to summarize!")
        else:
            st.session_state.summarized_dag = cached_summarize_dag(
                st.session_state.original_dag,
                size_constraint,
                semantic_threshold
            )
            st.success("DAG summarized!")
            st.write("**Summarized DAG Nodes:**", list(st.session_state.summarized_dag.nodes))
            st.write("**Summarized DAG Edges:**", list(st.session_state.summarized_dag.edges))

# -----------------------------
# 4. Sidebar: Compute Causal Effects
# -----------------------------
with st.sidebar.expander("4. Compute Causal Effects"):
    if st.session_state.original_dag:
        all_nodes = list(st.session_state.original_dag.nodes)
        if len(all_nodes) < 2:
            st.warning("Need at least two nodes to compute causal effects.")
        else:
            node1 = st.selectbox("Select Node 1:", all_nodes, key="node1")
            node2 = st.selectbox("Select Node 2:", all_nodes, key="node2")
            graph_choice = st.selectbox("Apply computation to:", ["Original Graph", "Summarized Graph"], key="graph_choice")
            compute_effect = st.button("Compute Causal Effect")
            if compute_effect:
                chosen_graph = st.session_state.original_dag if graph_choice == "Original Graph" else st.session_state.summarized_dag
                if chosen_graph:
                    # Placeholder
                    effect = 0.5
                    st.write(f"Causal effect of {node1} on {node2} in {graph_choice}: {effect} (placeholder)")
                else:
                    st.error("Selected graph is not available.")
    else:
        st.info("No DAG to compute effects on.")

# -----------------------------
# Main Page: 2 Columns
# -----------------------------
col1, col2 = st.columns([1,1])

# Left Column: Original DAG
with col1:
    st.subheader("Original Causal DAG")
    if st.session_state.original_dag:
        if is_valid_dag(st.session_state.original_dag):
            dag_html = visualize_dag_with_pyvis(
                st.session_state.original_dag,
                height="500px",
                width="600px"
            )
            components.html(dag_html, height=520, scrolling=False)
        else:
            st.warning("Not a valid DAG.")
    else:
        st.info("No original DAG.")

    # --- Expander for Edit Edges (with a pencil emoji)
    with st.expander("✏️ Edit Edges in Original DAG"):
        st.write("Add or remove edges by typing `Node1,Node2`. Then click **Apply**.")
        add_edge_input = st.text_input("Add edge (format: Node1,Node2)", key="add_edge_input", value="")
        remove_edge_input = st.text_input("Remove edge (format: Node1,Node2)", key="remove_edge_input", value="")
        apply_edits_btn = st.button("Apply Changes to Original DAG")

        if apply_edits_btn:
            # Add edges
            if add_edge_input.strip():
                try:
                    n1, n2 = [x.strip() for x in add_edge_input.split(",")]
                    st.session_state.original_dag.add_edge(n1, n2)
                    st.success(f"Edge ({n1} → {n2}) added.")
                except Exception as e:
                    st.error(f"Error adding edge: {e}")

            # Remove edges
            if remove_edge_input.strip():
                try:
                    n1, n2 = [x.strip() for x in remove_edge_input.split(",")]
                    if st.session_state.original_dag.has_edge(n1, n2):
                        st.session_state.original_dag.remove_edge(n1, n2)
                        st.success(f"Edge ({n1} → {n2}) removed.")
                    else:
                        st.warning(f"Edge ({n1} → {n2}) does not exist.")
                except Exception as e:
                    st.error(f"Error removing edge: {e}")

            # Force a re-run so the DAG re-renders
            st.experimental_rerun()

# Right Column: Summarized Graph
with col2:
    st.subheader("Summarized Graph")
    if st.session_state.summarized_dag:
        if is_valid_dag(st.session_state.summarized_dag):
            summ_html = visualize_dag_with_pyvis(
                st.session_state.summarized_dag,
                height="500px",
                width="600px"
            )
            components.html(summ_html, height=520, scrolling=False)
        else:
            st.warning("The summarized graph is not a valid DAG.")
    else:
        st.info("No summarized DAG available yet.")

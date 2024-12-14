import streamlit as st
import networkx as nx
from graph_utils import load_dag_from_file, generate_dag_algorithm
from summarization import summarize_dag
from visualization import visualize_dag_with_pyvis

# Initialize session state
if "original_dag" not in st.session_state:
    st.session_state.original_dag = None
if "summarized_dag" not in st.session_state:
    st.session_state.summarized_dag = None
if "dataset" not in st.session_state:
    st.session_state.dataset = None

st.set_page_config(page_title="Causal DAG Summarization Tool", layout="wide")

st.title("Causal DAG Summarization Tool")
st.markdown("### A UI for Summarizing and Interacting with Causal DAGs")

# --- Sidebar for inputs and configuration ---
st.sidebar.subheader("1. Upload Inputs")
dag_file = st.sidebar.file_uploader("Upload Causal DAG File (optional):")

if dag_file is not None:
    st.session_state.original_dag = load_dag_from_file(dag_file)
    st.sidebar.success("DAG uploaded successfully!")

data_file = st.sidebar.file_uploader("Upload Dataset File (optional):")
if data_file is not None:
    # For now, we don't do anything with the dataset except store it
    st.session_state.dataset = data_file.getvalue()
    st.sidebar.success("Dataset uploaded successfully!")

st.sidebar.markdown("Or, if no DAG is provided:")
generate_dag = st.sidebar.button("Generate DAG")
if generate_dag and st.session_state.original_dag is None:
    st.session_state.original_dag = generate_dag_algorithm()
    st.sidebar.success("DAG generated successfully!")
elif generate_dag and st.session_state.original_dag is not None:
    st.sidebar.info("A DAG is already loaded or generated.")

st.sidebar.subheader("2. Configuration Parameters")
size_constraint = st.sidebar.number_input("Size Constraint:", min_value=1, value=10)
semantic_threshold = st.sidebar.slider("Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05)

st.sidebar.subheader("3. Summarize DAG")
summarize_button = st.sidebar.button("Summarize Data")
if summarize_button:
    if st.session_state.original_dag is None:
        st.sidebar.warning("Please provide or generate a DAG before summarizing.")
    else:
        st.session_state.summarized_dag = summarize_dag(st.session_state.original_dag, size_constraint, semantic_threshold)
        st.sidebar.success("DAG summarized successfully!")

st.sidebar.markdown("---")
st.sidebar.subheader("4. Edit Summarized Graph")

if st.session_state.summarized_dag:
    add_edge_nodes = st.sidebar.text_input("Add edge (format: Node1,Node2):", value="")
    remove_edge_nodes = st.sidebar.text_input("Remove edge (format: Node1,Node2):", value="")
    apply_edits = st.sidebar.button("Apply Edits")
    if apply_edits:
        # Edge addition
        if add_edge_nodes:
            try:
                n1, n2 = [x.strip() for x in add_edge_nodes.split(",")]
                st.session_state.summarized_dag.add_edge(n1, n2)
                st.sidebar.success(f"Edge ({n1}->{n2}) added.")
            except:
                st.sidebar.error("Invalid format for adding edge.")
        # Edge removal
        if remove_edge_nodes:
            try:
                n1, n2 = [x.strip() for x in remove_edge_nodes.split(",")]
                if st.session_state.summarized_dag.has_edge(n1, n2):
                    st.session_state.summarized_dag.remove_edge(n1, n2)
                    st.sidebar.success(f"Edge ({n1}->{n2}) removed.")
                else:
                    st.sidebar.warning("That edge does not exist.")
            except:
                st.sidebar.error("Invalid format for removing edge.")

st.sidebar.markdown("---")
st.sidebar.subheader("5. Compute Causal Effects")

if st.session_state.original_dag is not None:
    all_nodes = list(st.session_state.original_dag.nodes)
    node1 = st.sidebar.selectbox("Select Node 1:", all_nodes, key="node1")
    node2 = st.sidebar.selectbox("Select Node 2:", all_nodes, key="node2")
    graph_choice = st.sidebar.selectbox("Apply computation to:", ["Original Graph", "Summarized Graph"], key="graph_choice")
    compute_effect = st.sidebar.button("Compute Causal Effect")
    if compute_effect:
        # Placeholder causal effect computation
        chosen_graph = st.session_state.original_dag if graph_choice == "Original Graph" else st.session_state.summarized_dag
        # Mock result
        st.sidebar.write(f"Causal effect of {node1} on {node2} in {graph_choice}: 0.5 (placeholder)")

# --- Main Page Visualizations ---
col1, col2 = st.columns(2)

col1.subheader("Original Causal DAG")
if st.session_state.original_dag is not None:
    html_str = visualize_dag_with_pyvis(st.session_state.original_dag)
    col1.components.v1.html(html_str, height=600)
else:
    col1.write("No original DAG available.")

col2.subheader("Summarized Graph")
if st.session_state.summarized_dag is not None:
    html_str = visualize_dag_with_pyvis(st.session_state.summarized_dag)
    col2.components.v1.html(html_str, height=600)
else:
    col2.write("No summarized DAG available yet.")

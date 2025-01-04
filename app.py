import streamlit as st
import networkx as nx
import logging
import streamlit.components.v1 as components
import pandas as pd

# Local modules
from graph_utils import (
    load_dag_from_file,
    generate_dag_algorithm,
    generate_dag_from_dataset,
    is_valid_dag,
    dict_of_dicts_to_numpy,
)
import graph_utils
from summarization import summarize_dag
from visualization import visualize_dag_with_pyvis, check_for_nonstring_attribute_keys
from semantic_coloring import colorize_nodes_by_similarity
import algo 
from Utils import ensure_string_labels
from graph_ops import try_add_edge, try_remove_edge

# ---------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger()

# ---------------------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="✨ Causal DAG Summarization Tool",
    layout="wide"
)

# ---------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------
def initialize_session_state():
    if "original_dag" not in st.session_state:
        st.session_state.original_dag = None
    if "summarized_dag" not in st.session_state:
        st.session_state.summarized_dag = None
    if "dataset" not in st.session_state:
        st.session_state.dataset = None

initialize_session_state()

# ---------------------------------------------------------------------
# Sidebar Logic
# ---------------------------------------------------------------------
def display_sidebar():
    with st.sidebar.expander("1. Upload or Generate DAG", True):
        dag_file = st.file_uploader("Upload Causal DAG File (.dot)", type=["dot"])
        data_file = st.file_uploader("Upload Dataset File (optional):")

        col_btns = st.columns([1,1])
        with col_btns[0]:
            gen_btn = st.button("Generate DAG")
        with col_btns[1]:
            reset_btn = st.button("Reset DAG")

        # Reset
        if reset_btn:
            st.session_state.original_dag = None
            st.session_state.summarized_dag = None
            st.info("DAG has been reset.")
            st.experimental_rerun()

        # If no DAG in memory, try loading or generating
        if st.session_state.original_dag is None:
            if dag_file is not None:
                loaded_dag = load_dag_from_file(dag_file)
                if loaded_dag:
                    st.session_state.original_dag = loaded_dag
                    st.success("DAG uploaded successfully!")
            elif data_file is not None and gen_btn:
                st.session_state.dataset = data_file.getvalue()
                new_dag = generate_dag_from_dataset(st.session_state.dataset)
                st.session_state.original_dag = new_dag
                st.success("DAG generated from dataset.")
            elif gen_btn and data_file is None:
                st.session_state.original_dag = generate_dag_algorithm()
                st.success("Placeholder DAG generated.")
        else:
            st.info("A DAG is already loaded. Click 'Reset DAG' to start fresh.")

    with st.sidebar.expander("2. Configuration Parameters"):
        if st.session_state.original_dag:
            st.session_state.size_constraint = st.number_input("Size Constraint:", min_value=1, value=35)
            st.session_state.semantic_threshold = st.slider("Semantic Similarity Threshold:", 0.0, 1.0, 0.5, 0.05)
        else:
            st.info("Please upload/generate a toy DAG in order to update summarization configuration")

    with st.sidebar.expander("Compute Causal Effects"):
        # 1) If no original DAG is loaded:
        if st.session_state.original_dag is None:
            st.error("No original DAG for computing ATE.")
        
        else:
            # 2) The user can choose which graph to use.
            graph_options = ["Original DAG"]
            if st.session_state.summarized_dag is not None:
                graph_options.append("Summarized DAG")

            chosen_graph_label = st.selectbox(
                "Select Graph:",
                graph_options,
                index=0
            )

            # Depending on the chosen graph, get the node list
            if chosen_graph_label == "Original DAG":
                chosen_graph = st.session_state.original_dag
            else:
                chosen_graph = st.session_state.summarized_dag

            nodes_list = list(chosen_graph.nodes())

            # 2.2) Let user pick Treatment/Outcome
            treatment = st.selectbox("Select Treatment:", nodes_list)
            outcome   = st.selectbox("Select Outcome:", nodes_list)

            # Finally, a button to compute ATE, etc.
            compute_button = st.button("Compute ATE")
            if compute_button:
                # Placeholder logic:
                st.write(f"Computing ATE of {chosen_graph_label} ...")
                # <Placeholder for calculating ATE logic>
                st.success("ATE computation is a placeholder for now!")

# ---------------------------------------------------------------------
# Display a DAG Column (PyVis + optional Edit Expander)
# ---------------------------------------------------------------------
def display_dag_column(title: str, dag: nx.DiGraph, is_original: bool = True):
    st.subheader(title)
    if dag is None:
        st.info(f"No {title.lower()} is currently available.")
        return

    if not is_valid_dag(dag):
        st.warning(f"The {title.lower()} is not a valid DAG.")
        return

    # colorize
    node_list = list(dag.nodes())
    _, _, color_map = colorize_nodes_by_similarity(node_list)

    # visualize
    modified_nodes_dag = ensure_string_labels(dag)
    # debug
    if not is_original:
        check_for_nonstring_attribute_keys(modified_nodes_dag)
    pyvis_dag = graph_utils.to_pyvis_compatible(modified_nodes_dag)
    html_str = visualize_dag_with_pyvis(
        G=pyvis_dag,
        color_map=color_map,
        height="600px",
        width="100%"
    )
    components.html(html_str, height=620, scrolling=False)

    # If it's the original DAG, allow editing
    if is_original:
        with st.expander("✏️ Edit Edges in Original DAG"):
            st.write("Use `Node1,Node2` format for adding/removing edges, then click **Apply**.")
            add_edge_txt = st.text_input("Add edge:", "")
            remove_edge_txt = st.text_input("Remove edge:", "")
            apply_btn = st.button("Apply Changes to Original DAG")

            if apply_btn:
                encountered_error = False

                # ADD edge logic
                if add_edge_txt.strip():
                    try:
                        n1, n2 = [x.strip() for x in add_edge_txt.split(",")]
                        success = try_add_edge(dag, n1, n2)
                        if not success:
                            encountered_error = True
                    except ValueError:
                        st.error("Invalid format: must be 'Node1,Node2'.")
                        encountered_error = True
                    except Exception as ex:
                        st.error(f"Error adding edge: {ex}")
                        encountered_error = True

                # REMOVE edge logic
                if remove_edge_txt.strip():
                    try:
                        n1, n2 = [x.strip() for x in remove_edge_txt.split(",")]
                        success = try_remove_edge(dag, n1, n2)
                        if not success:
                            encountered_error = True
                    except ValueError:
                        st.error("Invalid format: must be 'Node1,Node2'.")
                        encountered_error = True
                    except Exception as ex:
                        st.error(f"Error removing edge: {ex}")
                        encountered_error = True

                # only rerun if no errors
                if not encountered_error:
                    st.experimental_rerun()


        summarize_button = st.button("Summarize Casual DAG", key="summarize_button_left_col")
        if summarize_button:
            if st.session_state.original_dag is None:
                st.warning("Please provide or generate a DAG before summarizing.")
            else:
                with st.spinner("Summarizing DAG..."):
                    original_dag = st.session_state.original_dag
                    nodes_list = list(original_dag.nodes())
                    k_value = st.session_state.size_constraint
                    semantic_threshold = st.session_state.semantic_threshold
                    similarity_mat= dict_of_dicts_to_numpy(colorize_nodes_by_similarity(nodes_list)[0])
                    similarity_df = pd.DataFrame(similarity_mat, index=nodes_list, columns=nodes_list)

                    if not semantic_threshold:
                        summary_dag = algo.CaGreS(original_dag, k_value)
                    else:
                        summary_dag = algo.CaGreS(original_dag, k_value, similarity_df, semantic_threshold)

                    # Ensuring all edges, nodes in the graph contain only string attributes, whatever has non-string is being converted into string
                    summary_dag = ensure_string_labels(summary_dag)
                    graph_utils.fix_nested_keys_in_edge_attrs(summary_dag)

                    st.session_state.summarized_dag = summary_dag
                    st.success("DAG summarized successfully!")
                    st.experimental_rerun()

# ---------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------
def main():
    st.title("✨ Causal DAG Summarization Tool")
    st.markdown("""
    ### A UI for Summarizing and Interacting with Causal DAGs
    * Upload or generate an original DAG.
    * Summarize it, colorize nodes by semantic similarity.
    * Edit edges with safety checks (no self-loops, no cycles).
    * Placeholder for computing causal effects.
    """)

    display_sidebar()

    col1, col2 = st.columns([1,1])
    with col1:
        display_dag_column("Original Causal DAG", st.session_state.original_dag, is_original=True)
    with col2:
        display_dag_column("Summarized Graph", st.session_state.summarized_dag, is_original=False)

if __name__ == "__main__":
    main()

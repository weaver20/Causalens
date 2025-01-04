import streamlit as st
import networkx as nx
import logging
import streamlit.components.v1 as components
import pandas as pd

# Local imports
from graph_utils import (
    load_dag_from_file,
    generate_dag_algorithm,
    generate_dag_from_dataset,
    is_valid_dag,
    dict_of_dicts_to_numpy,
    to_pyvis_compatible,
    fix_nested_keys_in_edge_attrs
)
from visualization import visualize_dag_with_pyvis, check_for_nonstring_attribute_keys
from semantic_coloring import colorize_nodes_by_similarity
import algo  # The CaGreS algorithm module
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
    """Initialize Streamlit session_state variables if they don't exist yet."""
    if "original_dag" not in st.session_state:
        st.session_state.original_dag = None
    if "summarized_dag" not in st.session_state:
        st.session_state.summarized_dag = None
    if "dataset" not in st.session_state:
        st.session_state.dataset = None

# ---------------------------------------------------------------------
# Sidebar Functions
# ---------------------------------------------------------------------
def sidebar_upload_or_generate_dag():
    """
    Sidebar block #1: Upload or generate DAG.
    Provides .dot file upload, dataset upload, or DAG generation.
    Resets DAG on 'Reset DAG' click.
    """
    dag_file = st.file_uploader("Upload Causal DAG File (.dot)", type=["dot"])
    data_file = st.file_uploader("Upload Dataset File (optional):")

    col_btns = st.columns([1, 1])
    with col_btns[0]:
        gen_btn = st.button("Generate DAG")
    with col_btns[1]:
        reset_btn = st.button("Reset DAG")

    # Reset logic
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


def sidebar_configuration():
    """
    Sidebar block #2: Configuration Parameters.
    Lets user set size constraint and semantic threshold if a DAG is loaded.
    """
    if st.session_state.original_dag:
        st.session_state.size_constraint = st.number_input(
            "Size Constraint:",
            min_value=1,
            value=5,
            max_value=35
        )
        st.session_state.semantic_threshold = st.slider(
            "Semantic Similarity Threshold:",
            0.0, 1.0, 0.5, 0.05
        )
    else:
        st.info("Please upload/generate a DAG to configure summarization.")


def sidebar_compute_causal_effects():
    """
    Sidebar block #3: Compute Causal Effects.
    Lets user pick which graph (original or summarized, if available),
    then pick Treatment and Outcome to compute ATE (placeholder).
    """
    if st.session_state.original_dag is None:
        # No DAG present => show error
        st.error("No original DAG for computing ATE.")
        return

    # If we do have an original DAG, see if we also have a summarized DAG
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

    # Let user pick Treatment / Outcome
    treatment = st.selectbox("Select Treatment:", nodes_list)
    outcome = st.selectbox("Select Outcome:", nodes_list)

    # Button to compute ATE
    compute_button = st.button("Compute ATE")
    if compute_button:
        # Placeholder logic:
        st.write(f"Computing ATE on {chosen_graph_label} "
                 f"between {treatment} and {outcome} ...")
        # <Placeholder for calculating ATE logic>
        st.success("ATE computation is a placeholder for now!")


def display_sidebar():
    """
    Displays the entire left-hand sidebar with three sections:
      1) Upload/Generate DAG
      2) Configuration
      3) Compute Causal Effects
    """
    with st.sidebar.expander("1. Upload or Generate DAG", expanded=True):
        sidebar_upload_or_generate_dag()

    with st.sidebar.expander("2. Configuration Parameters"):
        sidebar_configuration()

    with st.sidebar.expander("Compute Causal Effects"):
        sidebar_compute_causal_effects()

# ---------------------------------------------------------------------
# Main Columns
# ---------------------------------------------------------------------
def display_dag_column(title: str, dag: nx.DiGraph, is_original: bool = True):
    """
    Renders one column for either the original or the summarized DAG.
    1. Check presence/validity
    2. Colorize DAG
    3. Convert to PyVis-compatible & visualize
    4. If original, show edge-edit & summarize button
    """
    st.subheader(title)

    if not _check_dag_and_show_info(dag, title):
        return

    dag_colored = _colorize_dag(dag, is_original)
    _visualize_dag_pyvis(dag_colored)

    if is_original:
        _edit_edges_expander(dag)
        _summarize_dag_button()


def _check_dag_and_show_info(dag: nx.DiGraph, title: str) -> bool:
    """Check if the DAG is present & valid, displaying warnings if not. Returns True if good."""
    if dag is None:
        st.info(f"No {title.lower()} is currently available.")
        return False

    if not is_valid_dag(dag):
        st.warning(f"The {title.lower()} is not a valid DAG.")
        return False

    return True


def _colorize_dag(dag: nx.DiGraph, check_attrs: bool) -> nx.DiGraph:
    """Colorize the DAG nodes, ensure string labels, and optionally check for non-string keys."""
    node_list = list(dag.nodes())
    _, _, color_map = colorize_nodes_by_similarity(node_list)

    dag_str_labels = ensure_string_labels(dag)

    # If it's the summarized DAG (or you prefer checking always), do:
    if not check_attrs:
        check_for_nonstring_attribute_keys(dag_str_labels)

    # We attach the color map as an attribute if desired, or just return them separately.
    # For now, let's store them in dag_str_labels.graph so we can retrieve them.
    dag_str_labels.graph["color_map"] = color_map
    return dag_str_labels


def _visualize_dag_pyvis(dag_str_labels: nx.DiGraph):
    """Convert to a PyVis-compatible DAG and visualize."""
    color_map = dag_str_labels.graph.get("color_map", {})
    pyvis_dag = to_pyvis_compatible(dag_str_labels)
    html_str = visualize_dag_with_pyvis(
        pyvis_dag, color_map=color_map, height="600px", width="100%"
    )
    components.html(html_str, height=620, scrolling=False)


def _edit_edges_expander(dag: nx.DiGraph):
    """Show the 'Edit Edges' expander for the original DAG."""
    with st.expander("✏️ Edit Edges in Original DAG"):
        st.write("Use `Node1,Node2` format for adding/removing edges, then click **Apply**.")
        add_edge_txt = st.text_input("Add edge:", "")
        remove_edge_txt = st.text_input("Remove edge:", "")
        apply_btn = st.button("Apply Changes to Original DAG")

        if apply_btn:
            encountered_error = False

            # Add edge
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

            # Remove edge
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

            if not encountered_error:
                st.experimental_rerun()


def _summarize_dag_button():
    """
    Show a 'Summarize Casual DAG' button. When clicked:
    - Retrieve original DAG from session_state
    - Run CaGreS with or without similarity
    - Fix nested keys & store in session
    - Rerun
    """
    if st.button("Summarize Casual DAG", key="summarize_button_left_col"):
        if st.session_state.original_dag is None:
            st.warning("Please provide or generate a DAG first.")
        else:
            with st.spinner("Summarizing DAG..."):
                original_dag = st.session_state.original_dag
                nodes_list = list(original_dag.nodes())
                k_value = st.session_state.size_constraint
                thr = st.session_state.semantic_threshold

                mat = dict_of_dicts_to_numpy(colorize_nodes_by_similarity(nodes_list)[0])
                similarity_df = pd.DataFrame(mat, index=nodes_list, columns=nodes_list)

                if not thr:
                    summary_dag = algo.CaGreS(original_dag, k_value)
                else:
                    summary_dag = algo.CaGreS(original_dag, k_value, similarity_df, thr)

                summary_dag = ensure_string_labels(summary_dag)
                fix_nested_keys_in_edge_attrs(summary_dag)

                st.session_state.summarized_dag = summary_dag
                st.success("DAG summarized successfully!")
                st.experimental_rerun()


# ---------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------
def render_main_header():
    """
    Renders the title and the introductory markdown on the main page.
    """
    st.title("✨ Causal DAG Summarization Tool")
    st.markdown("""
    ### Summarize a Causal DAG using the CaGreS Algorithm

    * **Upload** a `.dot` file (your DAG) or **generate** a sample DAG in one click.
    * **Configure** parameters (size constraint, semantic threshold) via the sidebar.
    * **Visualize** the DAG—nodes are automatically **colorized** for intuitive grouping.
    * **Add / Remove edges** in the DAG with built-in safety checks (no self-loops, no cycles).
    * **Summarize** the DAG using the **CaGreS** algorithm to get and visualize a summarized causal DAG.
    * **Compute Average Treatment Effect** on either the original or the summarized DAG's nodes.
    """)


def layout_main_columns():
    """
    Lays out the main two columns for the original DAG (left) and summarized DAG (right).
    """
    col1, col2 = st.columns([1, 1])
    with col1:
        display_dag_column("Causal Toy DAG", st.session_state.original_dag, is_original=True)
    with col2:
        display_dag_column("Summarized Casual DAG", st.session_state.summarized_dag, is_original=False)


def main():
    """
    The main function orchestrating the entire app's flow.
    """
    # 1) Initialize session state
    initialize_session_state()

    # 2) Render the main header
    render_main_header()

    # 3) Display the sidebar (upload/generate, config, compute effects)
    display_sidebar()

    # 4) Layout the main two columns for DAG visualization
    layout_main_columns()


if __name__ == "__main__":
    main()

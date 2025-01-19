import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
from utils.graph_utils import to_pyvis_compatible
from utils.visualization import visualize_dag_with_pyvis
from utils.semantic_coloring import colorize_nodes_by_similarity, colorize_cluster_nodes
from dag_display.edge_edit import edit_edges_expander
from utils.graph_utils import is_valid_dag
from Utils import convert_nodes_snake_to_pascal_case

def display_dag_column(title: str, dag: nx.DiGraph, is_original: bool = True):
    st.subheader(title)

    if not _check_dag(dag, title):
        return
    dag = convert_nodes_snake_to_pascal_case(dag)
    color_map = _colorize_nodes(dag)
    pyvis_dag = to_pyvis_compatible(dag)

    if is_original:
        st.session_state.original_color_map = color_map
        html_str = visualize_dag_with_pyvis(pyvis_dag, color_map=color_map, original_dag=is_original)

    else:
        cluster_nodes_color_map = colorize_cluster_nodes(list(dag.nodes), st.session_state.original_color_map)
        html_str = visualize_dag_with_pyvis(pyvis_dag, color_map=cluster_nodes_color_map, original_dag=is_original)

    components.html(html_str, height=620, scrolling=False)

    if is_original:
        edit_edges_expander(dag)

        if st.button("Summarize Causal DAG", key="summarize_button_left_col"):
            st.session_state.summarize_button = True
            st.rerun()

def _check_dag(dag, title) -> bool:
    if dag is None:
        st.info(f"No {title.lower()} is currently available.")
        return False
    if not is_valid_dag(dag):
        st.warning(f"{title} is not a valid DAG.")
        return False
    return True

def _colorize_nodes(dag: nx.DiGraph):
    nodes = list(dag.nodes())
    _, _, c_map = colorize_nodes_by_similarity(nodes)
    return c_map

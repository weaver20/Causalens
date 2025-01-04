import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
from utils.graph_utils import to_pyvis_compatible
from utils.visualization import visualize_dag_with_pyvis, check_for_nonstring_attribute_keys
from utils.semantic_coloring import colorize_nodes_by_similarity
from Utils import ensure_string_labels
from dag_display.edge_edit import edit_edges_expander
from dag_display.summarize_button import summarize_dag_button
from utils.graph_utils import is_valid_dag

def display_dag_column(title: str, dag: nx.DiGraph, is_original: bool = True):
    st.subheader(title)

    if not _check_dag(dag, title):
        return

    dag_str = ensure_string_labels(dag)
    if not is_original:
        check_for_nonstring_attribute_keys(dag_str)

    color_map = _colorize_nodes(dag_str)
    pyvis_dag = to_pyvis_compatible(dag_str)
    html_str = visualize_dag_with_pyvis(pyvis_dag, color_map=color_map)

    components.html(html_str, height=620, scrolling=False)

    if is_original:
        edit_edges_expander(dag)
        summarize_dag_button()

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

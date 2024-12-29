import networkx as nx
from networkx.drawing.nx_agraph import read_dot
import streamlit as st
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

def is_valid_dag(G: nx.DiGraph):
    """
    Check if the provided graph is a valid Directed Acyclic Graph (DAG).
    """
    is_dag = nx.is_directed_acyclic_graph(G)
    logger.debug(f"Graph validation result: {is_dag}")
    return is_dag

def load_dag_from_file(file):
    """
    Loads a DAG from a DOT file by saving it to a temporary file and passing 
    the file path to read_dot().
    """
    try:
        content = file.getvalue().decode("utf-8")
        logger.debug("Received DOT file content for parsing.")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.dot') as tmp_file:
            tmp_file.write(content.encode('utf-8'))
            temp_filepath = tmp_file.name
            logger.debug(f"Temporary DOT file created at: {temp_filepath}")

        # Parse the DOT file using the file path
        G = read_dot(temp_filepath)
        DG = nx.DiGraph(G)

        if not is_valid_dag(DG):
            st.warning("The uploaded graph is not a valid Directed Acyclic Graph (DAG). Visualization may not be accurate.")
            logger.warning("Uploaded graph is not a valid DAG.")
        else:
            logger.info("Uploaded graph is a valid DAG.")

        return DG

    except Exception as e:
        st.error(f"An error occurred while loading the DOT file: {e}")
        logger.exception("Exception occurred while loading DOT file: %s", e)
        return None

    finally:
        # Clean up the temporary file
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            logger.debug(f"Temporary DOT file {temp_filepath} deleted.")

def generate_dag_algorithm():
    """
    Generates a simple DAG as a placeholder.
    """
    logger.debug("Generating a placeholder DAG (no dataset).")
    G = nx.DiGraph()
    G.add_nodes_from(["A", "B", "C"])
    G.add_edges_from([("A", "B"), ("B", "C")])
    logger.info(f"Placeholder DAG generated with nodes: {list(G.nodes)} and edges: {list(G.edges)}")
    return G

def generate_dag_from_dataset(dataset_bytes):
    """
    Example: generate a DAG from the provided dataset.
    Replace this with your real logic as needed.
    """
    logger.debug("Generating DAG from dataset (placeholder logic).")
    # For demonstration, we just create two nodes and one edge
    G = nx.DiGraph()
    G.add_nodes_from(["DatasetNode1", "DatasetNode2"])
    G.add_edge("DatasetNode1", "DatasetNode2")
    logger.info(f"DAG from dataset generated with nodes: {list(G.nodes)} and edges: {list(G.edges)}")
    return G

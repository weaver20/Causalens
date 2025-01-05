import networkx as nx
import streamlit as st

def try_add_edge(G: nx.DiGraph, n1: str, n2: str) -> bool:
    """
    Attempt to add an edge (n1->n2) to the DAG G.
    Returns True if the operation is successful, False if any error occurs.

    This checks:
      - Self-loop (n1 == n2)
      - Whether the edge already exists
      - Whether adding this edge creates a cycle (thus invalid for a DAG)
    """
    # 1) Self-loop check
    if n1 == n2:
        st.error("Cannot add a self-loop edge.")
        return False

    # 2) Check if edge already exists or nodes do not exist
    if G.has_edge(n1, n2):
        st.error(f"Edge ({n1}->{n2}) already exists.")
        return False
    
    if not G.has_node(n1):
        st.error(f"Node {n1} does not exist.")
        return False
    
    if not G.has_node(n2):
        st.error(f"Node {n2} does not exist.")
        return False

    # 3) Attempt to add
    G.add_edge(n1, n2)

    # 4) Check if we’re still a DAG
    if not nx.is_directed_acyclic_graph(G):
        # revert
        G.remove_edge(n1, n2)
        st.error(f"Adding edge ({n1}->{n2}) creates a cycle! Denied.")
        return False

    # otherwise, success
    st.success(f"Edge ({n1}->{n2}) added.")
    return True

def try_remove_edge(G: nx.DiGraph, n1: str, n2: str) -> bool:
    """
    Attempt to remove an edge (n1->n2) from the DAG G.
    Returns True if removal is successful, False otherwise.

    Checks whether the edge actually exists first.
    """
    if G.has_edge(n1, n2):
        G.remove_edge(n1, n2)
        st.success(f"Edge ({n1}->{n2}) removed.")
        return True
    else:
        st.error(f"Edge ({n1}->{n2}) does not exist. Try again.")
        return False

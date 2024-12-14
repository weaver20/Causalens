import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

def visualize_dag_with_pyvis(G: nx.DiGraph, height="600px"):
    """
    Visualize a NetworkX DiGraph using PyVis and return the HTML as a string.
    """
    net = Network(directed=True, height=height, width="100%", notebook=False)
    net.from_nx(G)
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {
          "iterations": 200
        }
      }
    }
    """)

    # Use a temporary file to save and read HTML
    net.save_graph("temp_graph.html")
    with open("temp_graph.html", "r", encoding="utf-8") as f:
        html_str = f.read()
    return html_str

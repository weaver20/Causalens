import networkx as nx
from pyvis.network import Network
import logging

logger = logging.getLogger(__name__)

def visualize_dag_with_pyvis(G: nx.DiGraph, height="500px", width="600px"):
    """
    Visualize a NetworkX DiGraph using PyVis and return the HTML as a string.
    We'll:
      - Use a Barnes-Hut layout
      - Mark edges as directed with arrowheads
      - Style nodes/edges for a professional black/white scheme
      - Provide "physics" controls
    """
    try:
        logger.debug("Initializing PyVis network visualization (directed).")

        net = Network(
            height=height,
            width=width,
            directed=True,
            notebook=False
        )
        net.from_nx(G)

        # Style nodes
        for node in net.nodes:
            node["shape"] = "circle"
            node["color"] = {
                "border": "black",
                "background": "white",
                "highlight": {
                    "border": "black",
                    "background": "#e5e5e5"
                }
            }
            node["borderWidth"] = 2
            node["borderWidthSelected"] = 4
            node["font"] = {
                "size": 18,
                "color": "black",
                "face": "arial",
            }

        # Style edges
        for edge in net.edges:
            edge["arrows"] = "to"
            edge["color"] = "black"
            edge["width"] = 2

        net.barnes_hut(
            central_gravity=0.0,
            spring_length=200,
            spring_strength=0.05,
            damping=0.09,
            overlap=0
        )

        html_str = net.generate_html(notebook=False)
        return html_str

    except Exception as e:
        logger.exception(f"Error during PyVis visualization: {e}")
        return f"<p>Error rendering PyVis graph: {e}</p>"

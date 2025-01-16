import networkx as nx
from pyvis.network import Network
import logging

logger = logging.getLogger(__name__)

def check_for_nonstring_attribute_keys(G):
    """
    Scans node attributes, edge attributes, and G.graph
    to see if any dictionary has a non-string key.
    """

    # 1) Check global graph attributes in G.graph
    for k, v in list(G.graph.items()):
        if not isinstance(k, str):
            print(f"[GRAPH ATTR] Non-string key in G.graph: {k} (type: {type(k)}) => {v}")

    # 2) Check node attributes
    for node, data in G.nodes(data=True):
        # data is a dictionary of node attributes
        for k, v in list(data.items()):
            if not isinstance(k, str):
                print(f"[NODE ATTR] Non-string key for node {node}: {k} (type: {type(k)}) => {v}")
            # also check if 'v' itself might be a dictionary with non-string keys, etc.
            if isinstance(v, dict):
                for subk, subv in v.items():
                    if not isinstance(subk, str):
                        print(f"[NODE ATTR] Nested non-string key in node {node}'s dict: {subk} => {subv}")

    # 3) Check edge attributes
    for u, v, data in G.edges(data=True):
        for k, val in list(data.items()):
            if not isinstance(k, str):
                print(f"[EDGE ATTR] Non-string key for edge {u}->{v}: {k} (type: {type(k)}) => {val}")
            # If val is also a dict, check that recursively as well:
            if isinstance(val, dict):
                for subk, subv in val.items():
                    if not isinstance(subk, str):
                        print(f"[EDGE ATTR] Nested non-string key in edge {u}->{v}'s dict: {subk} => {subv}")


def _lighten_color(rgb_str, factor=0.4):
    """Same lightening function as before."""
    rgb_str = rgb_str.strip()
    prefix = "rgb("
    suffix = ")"
    c_str = rgb_str[len(prefix):-len(suffix)]
    parts = c_str.split(",")
    r, g, b = [int(p.strip()) for p in parts]
    nr = int(r + (255 - r)*factor)
    ng = int(g + (255 - g)*factor)
    nb = int(b + (255 - b)*factor)
    return f"rgb({nr},{ng},{nb})"

def visualize_dag_with_pyvis(G: nx.DiGraph,
                             original_dag,
                             color_map=None,
                             height="700px",
                             width="100%"):
    """
    Visualize a NetworkX DiGraph using PyVis, filling the column width (width="100%").
    We'll keep a fixed height for the net, but let it stretch horizontally.
    """
    try:
        logger.debug("Initializing PyVis network (directed).")
        net = Network(height=height, width=width, directed=True, notebook=False)
        H = G.copy()
        net.from_nx(H)

        # Style nodes
        for node in net.nodes:
            node["shape"] = "circle"
            node_id = node["id"]

            if not original_dag:
                node_id = node_id.replace('\n', '</b>,\n<b>')
            node["label"] = f"<b>{node_id}</b>"
            

            if color_map and node["id"] in color_map:
                base_color = color_map[node["id"]]
                lighter = _lighten_color(base_color, factor=0.4)
                node["color"] = {
                    "border": "black",
                    "background": lighter,
                    "highlight": {
                        "border": "black",
                        "background": "#e5e5e5"
                    }
                }
            else:
                node["color"] = {
                    "border": "black",
                    "background": "rgb(240,240,240)",
                    "highlight": {
                        "border": "black",
                        "background": "#e5e5e5"
                    }
                }
            node["borderWidth"] = 2
            node["borderWidthSelected"] = 4
            node["font"] = {
                "size": 20,
                "color": "black",
                "face": "arial",
                "bold": "18px",
                "multi": True,
            }

        # Style edges
        for edge in net.edges:
            edge["arrows"] = "to"
            edge["color"] = "black"
            edge["width"] = 2

        # Barnes-Hut layout
        net.barnes_hut(
            central_gravity=0.0,
            spring_length=200,
            spring_strength=0.05,
            damping=0.09,
            overlap=0
        )

        #net.toggle_physics(False)
        #net.set_edge_smooth('diagonalCross')
        

        html_str = net.generate_html(notebook=False)
        return html_str

    except Exception as e:
        logger.exception(f"Error during PyVis visualization: {e}")
        return f"<p>Error rendering PyVis graph: {e}</p>"
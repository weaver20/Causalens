import networkx as nx

def get_grounded_dag(summary_dag):
    nodes = list(nx.topological_sort(summary_dag))
    return get_grounded_dag_auxiliary(summary_dag, nodes)

def get_grounded_dag_auxiliary(summary_dag,nodes):
    """
    Copied from legacy Utils lib
    """
    G = summary_dag.copy()
    for n in summary_dag.nodes:
        if ',\n' in n:
            new_nodes = n.split(',\n')
            node_to_split = n

            # Identify parents and children of the original node
            parents = list(G.predecessors(node_to_split))
            children = list(G.successors(node_to_split))

            # Add edges between new nodes and parents/children
            for parent in parents:
                for new_node in new_nodes:
                    G.add_edge(parent, new_node)

            for child in children:
                for new_node in new_nodes:
                    G.add_edge(new_node, child)

            for new_node in new_nodes:
                for node_before in nodes:
                    if node_before not in n:
                        continue
                    if node_before == new_node:
                        break  # Stop connecting nodes once we reach the target node
                    G.add_edge(node_before, new_node)
            # Remove the original node
            G.remove_node(node_to_split)
    #show_dag(G,'grounded_dag')
    return G

def ensure_string_labels(G):
    """
    Force every node in the DAG G to have a string name
    (avoid tuple or set node-ids which break PyVis)
    """
    # We make a copy if you want to avoid in-place changes:
    # G = G.copy()
    
    mapping = {}
    for node in list(G.nodes()):
        if not isinstance(node, str):
            # Convert non-str node to a string
            node_str = (
                node 
                if isinstance(node, str) 
                else ",\n".join(str(x) for x in node)
            )
            mapping[node] = node_str
    
    if mapping:
        G = nx.relabel_nodes(G, mapping)
    return G

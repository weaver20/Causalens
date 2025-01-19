import networkx as nx
import re
import pandas as pd

TOKEN_PATTERN = r"""
        (?P<LPAREN>\() |
        (?P<RPAREN>\)) |
        (?P<NOT>NOT\b) |
        (?P<AND>AND\b) |
        (?P<OR>OR\b) |
        (?P<COND>(?P<NODE>[A-Za-z0-9_]+)\s*(?P<OP>==|!=|<=|>=|<|>)\s*(?P<VAL>("[^"]*"|'[^']*'|[A-Za-z0-9_.]+)))
    """

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

def is_valid_condition(expr: str, valid_nodes: list[str]):
    """
    Validate a logic expression that may contain:
      - Atomic conditions: NodeName <op> literal
        where <op> in (==, !=, <=, >=, <, >)
      - AND, OR, NOT
      - Parentheses grouping
    Example:
      (NumColumns <= 5) AND (Age > 20) OR NOT (Gender == 'F')

    Return (True, "") if valid, else (False, errorMessage).
    """

    expr = expr.strip()
    if not expr:
        return (False, "Empty expression.")

    tokens = []
    for match in re.finditer(TOKEN_PATTERN, expr, re.VERBOSE):
        kind = match.lastgroup
        text = match.group(kind)
        if kind == 'COND':
            node_name = match.group("NODE")
            op = match.group("OP")
            val = match.group("VAL")

            if node_name not in valid_nodes:
                return (False, f"Unknown node '{node_name}' in condition.")

            tokens.append(("COND", node_name, op, val))
        else:
            tokens.append((kind, text))

    # consumed_len = sum(len(m.group(0)) for m in re.finditer(TOKEN_PATTERN, expr, re.VERBOSE))

    check_expr = re.sub(TOKEN_PATTERN, '', expr, flags=re.VERBOSE)
    if not re.fullmatch(r"\s*", check_expr):
        return (False, f"Unrecognized portion in expression: {check_expr.strip()}")

    if not tokens:
        return (False, "No valid tokens found in expression.")

    paren_stack = []
    for t in tokens:
        kind = t[0]
        if kind == "LPAREN":
            paren_stack.append("(")
        elif kind == "RPAREN":
            if not paren_stack:
                return (False, "Unmatched closing parenthesis.")
            paren_stack.pop()

    if paren_stack:
        return (False, "Unmatched opening parenthesis.")

    return (True, "")

def convert_df_columns_snake_to_pascal_inplace(df: pd.DataFrame):
    """
    In-place conversion of all column names from snake_case to PascalCase.
    e.g. 'result_cache_hit' -> 'ResultCacheHit'.
    """
    df_copy = df.copy()
    def to_pascal_case(snake: str):
        # Split by underscores, capitalize each part, then join
        parts = snake.split("_")
        return "".join(word.capitalize() for word in parts)

    df_copy.rename(columns=lambda col: to_pascal_case(col), inplace=True)
    return df_copy

def convert_nodes_pascal_to_snake_case_inplace(G: nx.Graph):
    def is_snake_case(s: str) -> bool:

        return bool(re.match(r'^[a-z0-9]+(?:_[a-z0-9]+)*$', s))

    def pascal_to_snake(s: str) -> str:
        # e.g., "QueryTemplate" -> "query_template"
        return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

    mapping = {}
    for node in list(G.nodes()):
        if isinstance(node, str) and not is_snake_case(node):
            new_label = pascal_to_snake(node)
            mapping[node] = new_label

    if mapping:
        nx.relabel_nodes(G, mapping, copy=False)

def convert_nodes_snake_to_pascal_case(old_graph: nx.Graph) -> nx.Graph:
    def snake_to_pascal(name: str) -> str:
        """Convert a snake_case string to PascalCase."""
        return "".join(part.capitalize() for part in name.split("_"))

    # Detect if the old graph is directed or not
    if old_graph.is_directed():
        new_graph = nx.DiGraph()
    else:
        new_graph = nx.Graph()

    # Map old node -> new node
    node_mapping = {}
    for node in old_graph.nodes:
        # If it has underscores, convert to PascalCase;
        # otherwise, leave it unchanged
        if "_" in str(node):
            new_node = snake_to_pascal(str(node))
        else:
            new_node = str(node)
        node_mapping[node] = new_node

    # Add nodes to the new graph with updated names and copied attributes
    for old_node, new_node in node_mapping.items():
        new_graph.add_node(new_node, **old_graph.nodes[old_node])
        # Optionally store the old name, if needed
        new_graph.nodes[new_node]["old_name"] = old_node

    # Add edges to the new graph, mapping old endpoints to new ones
    for u, v, data in old_graph.edges(data=True):
        new_u = node_mapping[u]
        new_v = node_mapping[v]
        new_graph.add_edge(new_u, new_v, **data)

    return new_graph

def convert_underscores_to_asterisks_inplace(df: pd.DataFrame):
    """
    Replaces underscores ('_') with asterisks ('*') in both columns and index, in place.
    """
    df.rename(
        columns=lambda col: col.replace("_", "*"),
        index=lambda idx: idx.replace("_", "*"),
        inplace=True
    )

def convert_ast_underscore_nodes(old_graph: nx.Graph) -> nx.Graph:
    """
    Create a new graph where each node name of the form:
        e.g. "result*cache*hit_execution*time"
    is converted to something like:
        "ResultCacheHit,\nExecutionTime"
    following this procedure:
    1) Split the node name on underscore (_).
    2) For each underscore-chunk, split on asterisk (*),
       capitalize each sub-chunk, then join them together.
    3) Join the underscore-chunks with ',\\n'.
    Returns the new graph (does not modify the old one in-place).
    """
    
    def convert_node_name(old_name: str) -> str:
        # Split by underscore
        underscore_parts = old_name.split('_')
        new_parts = []
        for part in underscore_parts:
            # Split each underscore-part by asterisk
            asterisk_subparts = part.split('*')
            # Capitalize each asterisk subpart and concatenate
            capitalized = "".join(sub.capitalize() for sub in asterisk_subparts)
            new_parts.append(capitalized)
        # Join the underscore-based chunks with ",\n"
        return ",\n".join(new_parts)

    # Preserve the graph type (directed / undirected)
    if old_graph.is_directed():
        new_graph = nx.DiGraph()
    else:
        new_graph = nx.Graph()

    # Build a mapping from old node to new node name
    node_mapping = {}
    for node in old_graph.nodes():
        new_node_name = convert_node_name(str(node))
        node_mapping[node] = new_node_name

    # Add nodes with new names, copying all attributes
    for old_node, new_node in node_mapping.items():
        new_graph.add_node(new_node, **old_graph.nodes[old_node])
        # If you want to keep track of the original name in an attribute:
        new_graph.nodes[new_node]['old_name'] = old_node

    # Add edges with updated node names, copying edge attributes
    for u, v, data in old_graph.edges(data=True):
        new_u = node_mapping[u]
        new_v = node_mapping[v]
        new_graph.add_edge(new_u, new_v, **data)

    return new_graph

def prepare_graph_format(G):
    """
    Builds a graph with a proper format for running the CaGreS summarization algorithm on.
    Inputs:
      G (nx.DiGraph)   : The original causal DAG.
    Returns:
      A DAG (NetworkX DiGraph) where each node has a '*' in its name instead of '_'.
    """
    d = {x: x.replace("_", "*") for x in list(G.nodes)}
    H = nx.relabel_nodes(G, d)
    return H


############### Graph Algo Utilities ###############

def semantic_sim(n1, n2, similarity_df, semantic_threshold):
    if similarity_df is not None:
        sim = max(similarity_df[n1][n2], similarity_df[n2][n1])
        if sim < semantic_threshold:
            return False
    return True

def a_valid_pair(node1, node2, similarity_df, summary_dag, semantic_threshold):
    if not check_semantic_for_cluster_nodes(node1, node2,similarity_df, semantic_threshold):
        return False
    G = summary_dag.copy()
    if summary_dag.has_edge(node1,node2):
        G.remove_edge(node1, node2)

    elif summary_dag.has_edge(node2,node1):
        G.remove_edge(node2, node1)

    if nx.has_path(G, node1, node2):
        length =  nx.shortest_path_length(G, node1, node2)
        if length >= 2:
        # paths = nx.all_simple_paths(summary_dag, node1, node2)
        # path_exists = any(len(path) >= 3 for path in paths)
        # if path_exists:
            return False
    elif nx.has_path(G, node2, node1):
        length = nx.shortest_path_length(G, node2, node1)
        if length >= 2:
            # #and nx.shortest_path_length(dag, node1, node2) >= 2:
            # paths = nx.all_simple_paths(summary_dag, node2, node1)
            # path_exists = any(len(path) >= 3 for path in paths)
            # if path_exists:
                return False
    return True

def check_semantic_for_cluster_nodes(node1, node2, similarity_df, semantic_threshold):
    nodes1 = node1.split('_')
    nodes2 = node2.split('_')
    # print("check valid pair: ", nodes1,nodes2)
    # print(similarity_df)
    if similarity_df is None:
        return True
    for n1 in nodes1:
        for n2 in nodes2:
            sim = max(similarity_df[n1][n2], similarity_df[n2][n1])
            if sim < semantic_threshold:
                return False
    return True
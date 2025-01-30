from dowhy import CausalModel
import causallearn.utils.GraphUtils as GU
from causallearn.search.ConstraintBased import PC
import math
import networkx as nx
import itertools
import random
import pandas as pd
import Utils
from utils import graph_utils
import itertools

def is_special_pair(graph, node1, node2):
    # Check if there is an edge between node1 and node2
    if graph.has_edge(node1, node2):
        # Check if node1 has no outgoing edges and node2 has one incoming and one outgoing edge
        if graph.out_degree(node1) == 0 and graph.in_degree(node2) == 1 and graph.out_degree(node2) == 1:
            return True
        if graph.out_degree(node2) == 0 and graph.in_degree(node1) == 1 and graph.out_degree(node1) == 1:
            return True
        if graph.in_degree(node1) == 0 and graph.in_degree(node2) == 1 and graph.out_degree(node2) == 1:
            return True
        if graph.in_degree(node2) == 0 and graph.in_degree(node1) == 1 and graph.out_degree(node1) == 1:
            return True
    return False

def low_cost_merges(dag, similarity_df, not_valid, semantic_threshold):
    nodes = dag.nodes()
    to_merge = []
    node_pairs = sorted(list(itertools.combinations(sorted(nodes), 2)))
    for pair in node_pairs:
        n1 = pair[0]
        n2 = pair[1]
        if not Utils.a_valid_pair(n1, n2, similarity_df, dag, semantic_threshold):
            not_valid.add(pair)
            continue
        if not n1 == n2:
            if '_' in n1 or '_' in n2:
                continue
            if Utils.semantic_sim(n1, n2, similarity_df, semantic_threshold):
                if is_special_pair(dag, n1, n2):
                    to_merge.append((n1, n2))
                elif zero_cost(dag, n1, n2):
                    to_merge.append((n1, n2))

    G = dag.copy()
    for pair in to_merge:
        node1 = pair[0]
        node2 = pair[1]
        if node1 in G.nodes and node2 in G.nodes:
            G = nx.contracted_nodes(G, node1, node2, self_loops=False)
            new_node_name = node1 + '_' + node2
            G = nx.relabel_nodes(G, {node1: str(new_node_name), node2: str(new_node_name)})

    return G, not_valid

def zero_cost(G, n1, n2):
    if G.has_edge(n1, n2) or G.has_edge(n2,n1):
        parents1 = set(G.predecessors(n1))
        if n2 in parents1:
            parents1.remove(n2)
        parents2 = set(G.predecessors(n2))
        if n1 in parents2:
            parents2.remove(n1)

        children1 = set(G.successors(n1))
        if n2 in children1:
            children1.remove(n2)
        children2 = set(G.successors(n2))
        if n1 in children2:
            children2.remove(n1)
        return parents1 == parents2 and children1 == children2
    else:
        parents1 = set(G.predecessors(n1))
        parents2 = set(G.predecessors(n2))
        children1 = set(G.successors(n1))
        children2 = set(G.successors(n2))
        return parents1 == parents2 and children1 == children2



def CaGreS(dag, k, similarity_df, semantic_threshold):
    """
    Implements Algorithm 1 (CaGreS) from the paper
    Inputs:
      dag (nx.DiGraph) : The original causal DAG.
      k (int)          : Target number of summary nodes.
      similarity_df    : (Optional) A DataFrame or dict with semantic similarities.
    
    Returns:
      A summary DAG (NetworkX DiGraph) with k (or fewer) nodes.
    """
    if len(dag.nodes) <= k:
        return dag
    not_valid = set()
    G, not_valid = low_cost_merges(dag, similarity_df, not_valid, semantic_threshold)

    cost_scores = {}
    while len(G.nodes) > k:
        G, not_valid, cost_scores = fast_merge_pair(G, dag, similarity_df,
                                                     not_valid, cost_scores,
                                                     semantic_threshold)
        
        # Fallback, could not summarize the DAG with given constraints
        if not G:
            break
    return G

def fast_merge_pair(G, dag, similarity_df, not_valid, cost_scores, semantic_threshold, verbos = False):
    node_pairs = sorted(list(itertools.combinations(sorted(G.nodes()), 2)))
    min_cost   = math.inf
    max_pair   = []

    for pair in node_pairs:
        node1 = pair[0]
        node2 = pair[1]
        if pair in not_valid:
            continue
        valid = Utils.a_valid_pair(node1,node2, similarity_df, G, semantic_threshold)
        if valid == False:
            not_valid.add(pair)
        else:
            if pair in cost_scores:
                cost = cost_scores[pair]
            else:
                cost = get_cost(node1,node2,G)
                cost_scores[pair] = cost
            if verbos:
                print(pair,cost)
            if cost < min_cost:
                min_cost = cost
                max_pair = pair
            elif cost == min_cost:
                if random.choice([True, False]):
                    min_cost = cost
                    max_pair = pair
    if len(max_pair) == 0:
        print("could not find a pair to merge, merging a random valid pair")
        for pair in node_pairs:
            if pair in not_valid:
                continue
            if Utils.a_valid_pair(*pair, similarity_df, dag):
                max_pair = pair
            
        # Fallback
        if len(max_pair) == 0:
            return None, not_valid, cost_scores
    node1 = max_pair[0]
    node2 = max_pair[1]

    cost_scores = update_cost_scores(cost_scores, node1, node2, G)
    #print("choose to merge: ", node1,node2)
    G = nx.contracted_nodes(G, node1, node2, self_loops=False)
    new_node_name = node1 + '_' + node2
    G = nx.relabel_nodes(G, {node1: str(new_node_name), node2: str(new_node_name)})

    return G, not_valid, cost_scores

def update_cost_scores(cost_scores, node1, node2, G):
    nodes = [node1,node2]
    nodes = nodes + list(G.predecessors(node1)) + list(G.successors(node1))
    nodes = nodes + list(G.predecessors(node2)) + list(G.successors(node2))
    to_remove = []
    for k in cost_scores:
        for n in nodes:
            if n in k:
                to_remove.append(k)
                break
    filtered_dict = {key: value for key, value in cost_scores.items() if key not in to_remove}
    return filtered_dict

def get_cost(node1, node2,G):
    cost = 0
    nodes1 = node1.split('_')
    nodes2 = node2.split('_')
    #edges among the new cluster
    if not G.has_edge(node1, node2):
        cost = cost + len(nodes1)*len(nodes2)

    #edges to parents and children
    parents1 = set(G.predecessors(node1))
    parents2 = set(G.predecessors(node2))

    #unique parents of node1
    if node2 in parents1:
        parents1.remove(node2)
    parents1 = parents1 - parents2#[p for p in parents1 if not p in parents2]
    cost = cost + len(parents1)*len(nodes2)

    #parents1 = list(G.predecessors(node1))
    # unique parents of node2
    if node1 in parents2:
        parents2.remove(node1)
    parents2 = parents2-parents1#[p for p in parents2 if not p in parents1]
    cost = cost + len(parents2) * len(nodes1)

    children1 = set(G.successors(node1))
    children2 = set(G.successors(node2))
    # unique children of node1
    if node2 in children1:
        children1.remove(node2)
    children1 = children1 - children2#[p for p in children1 if not p in children1]
    cost = cost + len(children1) * len(nodes2)

    #children1 = list(G.successors(node1))
    # unique children of node2
    if node1 in children2:
        children2.remove(node1)
    children2 = children2 - children1#[p for p in children2 if not p in children1]
    cost = cost + len(children2) * len(nodes1)

    return cost

def estimate_binary_treatment_effect(df, treatment_column, logic_condition, outcome_column, graph:nx.DiGraph):
    if not nx.has_path(graph, treatment_column, outcome_column):
        return -1, -1
    # 1) Load the DataFrame and convert columns to PascalCase if needed
    df = Utils.convert_df_columns_snake_to_pascal_inplace(df)

    # 2) Back up the original values from the treatment column
    original_values = df[treatment_column].copy()

    # 3) Overwrite the column in-place with 0 or 1, according to logic_condition
    #    - Replace 'treatment_column' in the condition with the actual column name
    #    - Translate "AND" -> "&", "OR" -> "|" for pandas.eval, etc.
    parsed_condition = (
        logic_condition
        .replace("AND", "&")
        .replace("OR", "|")
    )

    # Evaluate the condition, set matching rows to 1
    matching_rows = df.eval(parsed_condition)
    df[treatment_column] = 0
    df.loc[matching_rows, treatment_column] = 1

    # 4) Build a DoWhy causal model using the altered treatment column
    graph_str = graph_utils.to_digraph_string(graph)
    model = CausalModel(
        data=df,
        treatment=treatment_column,
        outcome=outcome_column,
        graph=graph_str
    )

    # 5) Identify the effect
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)

    # 6) Estimate effect with a simple backdoor method (e.g. linear regression)
    causal_estimate_reg = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.linear_regression",
        test_significance=True,
    )

    # 7) Restore the original column values
    df[treatment_column] = original_values
    return causal_estimate_reg, causal_estimate_reg.test_stat_significance()['p_value']

def get_grounded_dag(summary_dag):
    nodes = list(nx.topological_sort(summary_dag))
    return get_grounded_dag_auxiliary(summary_dag, nodes)

def get_grounded_dag_auxiliary(summary_dag,nodes):
    """
    Logic copied from Utils Lib.
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

def discover_causal_dag(df: pd.DataFrame, alpha: float = 0.05, verbose: bool = False):
    """Run PC on a DataFrame, keep only the fully-directed edges (color='black'), and return a DAG."""
    causal_graph = PC.pc(df.values, alpha=alpha, verbose=verbose)
    causal_graph.to_nx_graph() 
    
    graph_int = causal_graph.nx_graph
    edges_to_remove = [(u, v) for u, v, d in graph_int.edges(data=True) if d.get('color') != 'b']
    graph_int.remove_edges_from(edges_to_remove)

    for _, _, data in graph_int.edges(data=True):
        data['color'] = 'black'
        
    mapping = {i: df.columns[i] for i in graph_int.nodes()}
    return nx.relabel_nodes(graph_int, mapping)


def debug_print(graph, matching_rows, treatment_column, outcome_column, parsed_condition):
    print("===============")
    graph_str = graph_utils.to_digraph_string(graph)
    print("matching rows : ")
    print(matching_rows)
    print("Graph: " + graph_str)
    print("treatment: " + treatment_column)
    print("outcome: " + outcome_column)
    print("condition: " + parsed_condition)
    print()
    print(f"{treatment_column} values " + ", ".join(df[treatment_column].astype(str)))
    print(f"{outcome_column} values " + ", ".join(df[outcome_column].astype(str)))
    #print("DF columns: " + ", ".join(df.columns.to_list()))
    print("===============")
import math
import networkx as nx
import itertools
import Utils
import random
from itertools import combinations

SEMANTIC_THRESHOLD = 0.0

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

def low_cost_merges(dag, similarity_df=None):
    """
    Implements "Merge node‐pairs in which their cost <= 1" (Algorithm 1, line 2).
    We do this one merge at a time in a loop (not all simultaneously),
    because each merge changes the graph and can affect subsequent costs.
    """
    G = dag.copy()

    # Keep trying until no more merges of cost <= 1 can be found
    while True:
        merged_something = False
        for (n1, n2) in itertools.combinations(list(G.nodes), 2):
            if not a_valid_pair(n1, n2, G, similarity_df):
                continue

            c = get_cost(n1, n2, G)
            if c <= 1:
                # Merge them immediately
                G = merge_nodes(G, n1, n2)
                merged_something = True
                # Because we changed the graph, start again
                break  
        if not merged_something:
            # No more merges with cost <= 1
            break
    return G

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



def CaGreS(dag, k, similarity_df=None):
    """
    Implements Algorithm 1 (CaGreS) from your paper.
    Inputs:
      dag (nx.DiGraph) : The original causal DAG.
      k (int)          : Target number of summary nodes.
      similarity_df    : (Optional) A DataFrame or dict with semantic similarities.
    
    Returns:
      A summary DAG (NetworkX DiGraph) with k (or fewer) nodes.
    """
    # Work on a copy so the original remains intact.
    H = dag.copy()

    # Step 2 of Algorithm 1: Merge node pairs whose cost <= 1.
    H = low_cost_merges(H, similarity_df)

    # Main loop: while we have more than k nodes, pick the min-cost valid pair to merge.
    while len(H.nodes) > k:
        min_cost = math.inf
        best_pair = None

        # Explore all pairs
        for (U, V) in itertools.combinations(H.nodes, 2):
            if not a_valid_pair(U, V, H, similarity_df):
                continue

            c = get_cost(U, V, H)

            # Keep the pair with the minimal cost
            if c < min_cost:
                min_cost = c
                best_pair = (U, V)
            elif math.isclose(c, min_cost, rel_tol=1e-9):
                # Tie-break randomly (Algorithm 1, line 13)
                if random.choice([True, False]):
                    best_pair = (U, V)

        # If no valid pair was found, break to avoid infinite loops
        if best_pair is None:
            break

        # Merge the best pair
        U, V = best_pair
        H = merge_nodes(H, U, V)

    return H

def a_valid_pair(U, V, H, similarity_df=None):
    """
    Checks if merging U, V would be valid (Algorithm 1, line 8, IsValidPair).
    1) Optional semantic check (like your code did)
    2) Check if merging them would create a directed cycle in H
    """
    # (A) Semantic check
    if not check_semantic(U, V, similarity_df):
        return False

    # (B) Cycle check: Merge them in a temporary graph, see if the result is still a DAG
    temp = H.copy()
    temp = merge_nodes(temp, U, V, self_loops=True)  # or self_loops=False, as desired
    if not nx.is_directed_acyclic_graph(temp):
        return False

    return True

def check_semantic(node1, node2, similarity_df):
    """
    If you want to filter merges that are semantically different, 
    you can implement that here. For now, it returns True if no df or 
    if all pairs are above a threshold.
    """
    if similarity_df is None:
        return True

    sub1 = node1.split(',\n')
    sub2 = node2.split(',\n')
    for s1 in sub1:
        for s2 in sub2:
            sim = max(similarity_df[s1][s2], similarity_df[s2][s1])
            if sim < SEMANTIC_THRESHOLD:
                return False
    return True

def merge_nodes(G, n1, n2, self_loops=False):
    """
    Merge n2 into n1 using nx.contracted_nodes, then rename the merged node 
    to a combined label "n1,\nn2".
    """
    merged = nx.contracted_nodes(G, n1, n2, self_loops=self_loops)
    new_label = n1 + ",\n" + n2
    merged = nx.relabel_nodes(merged, {n1: new_label})
    return merged

def not_in_ci(ci, nodes1,nodes2):
    nodes = ci[0].copy()
    nodes.update(ci[1])
    if len(ci[2]) > 0:
        nodes.update(ci[2])
    for n in nodes1:
        if n in nodes:
            return False
    for n in nodes2:
        if n in nodes:
            return False
    return True

def all_in(nodes,s):
    for n in nodes:
        if not n in s:
            return False
    return True

def get_similarity(node1,node2,recursive_basis):
    nodes1 = node1.split(',\n')
    nodes2 = node2.split(',\n')
    num_preserved = 0
    for ci in recursive_basis:
        if all_in(nodes1,ci[0]) and all_in(nodes2,ci[0]):
            num_preserved = num_preserved + 1
        elif all_in(nodes1, ci[1]) and all_in(nodes2, ci[1]):
            num_preserved = num_preserved + 1
        elif all_in(nodes1, ci[2]) and all_in(nodes2, ci[2]):
            num_preserved = num_preserved + 1
        elif not_in_ci(ci, nodes1,nodes2):
            num_preserved = num_preserved + 1
    return num_preserved

def merege_pair(G,recursive_basis,nodes,dag,similarity_df, verbos = False):
    node_pairs = itertools.combinations(G.nodes(), 2)
    max_sim = 0
    max_pair = []
    for pair in node_pairs:
        node1 = pair[0]
        node2 = pair[1]
        if Utils.a_valid_pair(node1,node2,dag, similarity_df):
            sim = get_similarity(node1,node2,recursive_basis)
            if verbos:
                print(pair,sim)
            if sim > max_sim:
                max_sim = sim
                max_pair = pair
            elif sim == max_sim:
                if random.choice(['True', 'False']):
                    max_sim = sim
                    max_pair = pair
    if len(max_pair) == 0:
        print("could not find a pair to merge, merging a random valid pair")
        for pair in node_pairs:
            node1 = pair[0]
            node2 = pair[1]
            if Utils.a_valid_pair(node1, node2, dag):
                max_pair = pair
    node1 = max_pair[0]
    node2 = max_pair[1]
    print("choose to merge: ", node1,node2)
    G = nx.contracted_nodes(G, node1, node2, self_loops=False)
    new_node_name = node1 + ',\n' + node2
    G = nx.relabel_nodes(G, {node1: str(new_node_name), node2: str(new_node_name)})
    recursive_basis = Utils.get_recursive_basis(G,nodes)
    return G, recursive_basis

def fast_merege_pair(G,nodes,dag,similarity_df,not_valid, cost_scores, verbos=False):
    node_pairs = itertools.combinations(G.nodes(), 2)
    min_cost =math.inf
    max_pair = []

    for pair in node_pairs:
        node1 = pair[0]
        node2 = pair[1]
        if pair in not_valid:
            continue
        valid = Utils.a_valid_pair(node1,node2,dag, similarity_df, G)
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
                if random.choice(['True', 'False']):
                    min_cost = cost
                    max_pair = pair
    if len(max_pair) == 0:
        print("could not find a pair to merge, merging a random valid pair")
        for pair in node_pairs:
            if pair in not_valid:
                continue
            node1 = pair[0]
            node2 = pair[1]
            if Utils.a_valid_pair(node1, node2, dag):
                max_pair = pair
    node1 = max_pair[0]
    node2 = max_pair[1]

    cost_scores = update_cost_scores(cost_scores, node1, node2, G)
    #print("choose to merge: ", node1,node2)
    node1_str = node1 if isinstance(node1, str) else ",\n".join(str(x) for x in node1)
    node2_str = node2 if isinstance(node2, str) else ",\n".join(str(x) for x in node2)
    new_node_name = node1_str + ",\n" + node2_str
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

def get_cost(U, V, H):
    """
    Implements Algorithm 2: The GetCost procedure.
    1) cost for "new edges" among the cluster
    2) cost for "new parents"
    3) cost for "new children"
    """
    # Determine how many "atomic" nodes each label represents
    subU = U.split(',\n')
    subV = V.split(',\n')
    sizeU = len(subU)
    sizeV = len(subV)

    cost = 0

    # (1) If H does NOT have edge U->V, add size(U)*size(V)
    #     (some variants also check if H does not have edge V->U, but typically it’s just the one direction)
    if not H.has_edge(U, V):
        cost += sizeU * sizeV

    # (2) "New parents" penalty
    parentsU = set(H.predecessors(U))
    parentsV = set(H.predecessors(V))
    parentsOnlyU = parentsU - parentsV
    parentsOnlyV = parentsV - parentsU
    cost += len(parentsOnlyU) * sizeV
    cost += len(parentsOnlyV) * sizeU

    # (3) "New children" penalty
    childrenU = set(H.successors(U))
    childrenV = set(H.successors(V))
    childrenOnlyU = childrenU - childrenV
    childrenOnlyV = childrenV - childrenU
    cost += len(childrenOnlyU) * sizeV
    cost += len(childrenOnlyV) * sizeU

    return cost

def update_recursive_basis(node1,node2,recursive_basis):
    updated_recursive_basis = []
    nodes1 = node1.split(',\n')
    nodes2 = node2.split(',\n')
    for ci in recursive_basis:
        if all_in(nodes1, ci[0]) and all_in(nodes2, ci[0]):
            updated_recursive_basis.append(ci)
        elif all_in(nodes1, ci[1]) and all_in(nodes2, ci[1]):
            updated_recursive_basis.append(ci)
        elif all_in(nodes1, ci[2]) and all_in(nodes2, ci[2]):
            updated_recursive_basis.append(ci)
        elif not_in_ci(ci, nodes1, nodes2):
            updated_recursive_basis.append(ci)
    return updated_recursive_basis



def check_edges_between_sets(graph, t1, t2):
    for edge in graph.edges():
        source, target = edge
        if (source in t1) and (target in t2):
            continue
        elif (source in t1) and (target in t1):
            continue
        elif (source in t2) and (target in t2):
            continue
        else:
            return False
    return True


def split_into_subsets(lst, threshold,dag):
    valid_splits = []
    for r in range(threshold , len(lst) - threshold):
        for combo in combinations(lst, r):
            complement = [item for item in lst if item not in combo]
            if len(combo) >= threshold and len(complement) >= threshold:
                valid = False
                if check_edges_between_sets(dag, list(combo), complement):
                    valid = True
                elif check_edges_between_sets(dag, complement,list(combo)):
                    valid = True
                if valid:
                    valid_splits.append((list(combo), complement))
    return valid_splits

def main():
    dag_edges = [('A', 'B'), ('A','C'),('C', 'D'),('B','D'), ('D', 'E')]
    dag = nx.DiGraph(dag_edges)
    k = 3
    nodes = ['A','B','C','D','E']
    recursive_basis = [(set(['C']), set(['B']), set(['A'])),
                       (set(['D']), set(['A']), set(['B','C'])),
                       (set(['E']), set(['A', 'B','C']), set('D'))]

    # summary_dag = greedy(dag,nodes, recursive_basis,k,None)
    # Utils.show_dag(summary_dag)
    import Examples
    from cProfile import Profile
    from pstats import SortKey, Stats
    dag, k, nodes, recursive_basis, similarity_df = Examples.random_dag(60, 0.2)
    k = 40

    #summary_dag_greedy, recursive_basis_greedy = greedy(dag, nodes, recursive_basis, k, similarity_df)
    with Profile() as profile:
        print(greedy(dag, nodes, recursive_basis, k, similarity_df))
        (
            Stats(profile)
            .strip_dirs()
            .sort_stats(SortKey.TIME)
            .print_stats()
        )
    # Example usage:


if __name__ == '__main__':
    main()
import streamlit as st
import pandas as pd
from algorithms import algo
from utils.graph_utils import dict_of_dicts_to_numpy, fix_nested_keys_in_edge_attrs
from utils.semantic_coloring import colorize_nodes_by_similarity
from Utils import ensure_string_labels, convert_nodes_pascal_to_snake_case_inplace
import Utils

def summarize_dag_button():
    if st.button("Summarize Causal DAG", key="summarize_button_left_col"):
        if st.session_state.original_dag is None:
            st.warning("Please upload/generate a DAG first.")
        else:
            with st.spinner("Summarizing DAG..."):
                convert_nodes_pascal_to_snake_case_inplace(st.session_state.original_dag)
                original_dag = st.session_state.original_dag
                nodes_list = list(original_dag.nodes())
                k_value = st.session_state.size_constraint
                thr = st.session_state.semantic_threshold

                mat = dict_of_dicts_to_numpy(colorize_nodes_by_similarity(nodes_list)[0])
                df = pd.DataFrame(mat, index=nodes_list, columns=nodes_list)

                # Ensuring graph and df match the algorithm input asssumptions
                G = Utils.prepare_graph_format(original_dag)
                Utils.convert_underscores_to_asterisks_inplace(df)

                summary_dag = algo.CaGreS(G, k_value, None if thr == 0.0 else df, thr)
                
                if summary_dag:
                    summary_dag = ensure_string_labels(summary_dag)
                    fix_nested_keys_in_edge_attrs(summary_dag)

                    st.session_state.summarized_dag = Utils.convert_ast_underscore_nodes(summary_dag)
                    st.success("DAG summarized successfully!")
                    st.rerun()
                
                else:
                    st.warning("Could not summarize DAG with given constraints!")

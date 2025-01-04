import streamlit as st
from algorithms.graph_ops import try_add_edge, try_remove_edge

def edit_edges_expander(dag):
    with st.expander("✏️ Edit Edges in Original DAG"):
        st.write("Use `Node1,Node2` format for adding/removing edges, then click **Apply**.")
        add_edge_txt = st.text_input("Add edge:", "")
        remove_edge_txt = st.text_input("Remove edge:", "")
        if st.button("Apply Changes to Original DAG"):
            err = False

            if add_edge_txt.strip():
                try:
                    n1, n2 = [x.strip() for x in add_edge_txt.split(",")]
                    if not try_add_edge(dag, n1, n2):
                        err = True
                except Exception as e:
                    st.error(f"Error adding edge: {e}")
                    err = True

            if remove_edge_txt.strip():
                try:
                    n1, n2 = [x.strip() for x in remove_edge_txt.split(",")]
                    if not try_remove_edge(dag, n1, n2):
                        err = True
                except Exception as e:
                    st.error(f"Error removing edge: {e}")
                    err = True

            if not err:
                st.experimental_rerun()

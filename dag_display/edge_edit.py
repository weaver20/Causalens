import streamlit as st
from algorithms.graph_ops import try_add_edge, try_remove_edge

def edit_edges_expander(dag):
    """
    An expander that lets the user pick a source and destination node
    from dropdowns, and choose to Add or Remove an edge.
    """
    all_nodes = sorted(list(dag.nodes()))
    if not all_nodes:
        return

    with st.expander("✏️ Edit Edges in Original DAG", expanded=False):
        st.write(
            "Use the dropdowns below to select the source and destination nodes. "
            "Then choose whether to **Add** or **Remove** the edge."
        )

        source_node = st.selectbox(
            "Source Node:",
            options=all_nodes,
            help="Pick the source node of the edge."
        )
        dest_node = st.selectbox(
            "Destination Node:",
            options=all_nodes,
            help="Pick the destination node of the edge."
        )

        edge_action = st.radio(
            "Action:",
            ["Add Edge", "Remove Edge"],
            horizontal=True,
            help="Choose whether to add or remove the edge."
        )

        if st.button("Apply Changes to Original DAG"):
            err = False
            try:
                if edge_action == "Add Edge":
                    if not try_add_edge(dag, source_node, dest_node):
                        err = True
                
                elif edge_action == "Remove Edge":
                    if not try_remove_edge(dag, source_node, dest_node):
                        err = True
            
            except Exception as e:
                st.error(f"Error modifying edge: {e}")
                err = True

            if not err:
                if edge_action == "Add Edge":
                    st.success("Added edge successfully!")
                if edge_action == "Remove Edge":
                    st.success("Removed edge successfully!")
                st.session_state.original_dag = dag
                st.session_state.summarized_dag = None
                st.rerun()

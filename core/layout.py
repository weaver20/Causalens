import streamlit as st
from dag_display.display_dag import display_dag_column

def render_main_header():
    st.title("✨ Causal DAG Summarization Tool")
    st.markdown("""
    ### Summarize a Causal DAG using the CaGreS Algorithm

    * **Upload** a `.dot` file or **generate** a sample DAG.
    * **Configure** size constraint & semantic threshold in the sidebar.
    * **Visualize** the DAG with color-coded nodes.
    * **Add / Remove edges** safely.
    * **Summarize** with CaGreS, then compute placeholder effects.
    """)

def layout_main_columns():
    c1, c2 = st.columns([1, 1])
    with c1:
        display_dag_column("Causal Toy DAG", st.session_state.original_dag, is_original=True)
    with c2:
        display_dag_column("Summarized Causal DAG", st.session_state.summarized_dag, is_original=False)

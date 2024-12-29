import networkx as nx
import plotly.graph_objs as go
import logging

logger = logging.getLogger(__name__)

def visualize_dag_with_plotly(G: nx.DiGraph, positions=None):
    """
    Visualize a NetworkX DiGraph using Plotly and return the figure.
    If 'positions' is provided, it should be a dict: {node: (x, y), ...}.
    """
    try:
        logger.debug("Initializing Plotly network visualization.")

        # If we haven't been given positions, generate them with spring_layout
        if positions is None:
            positions = nx.spring_layout(G, seed=42)

        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = positions[edge[0]]
            x1, y1 = positions[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_x = []
        node_y = []
        text_labels = []
        for node in G.nodes():
            x, y = positions[node]
            node_x.append(x)
            node_y.append(y)
            text_labels.append(str(node))

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=text_labels,
            textposition="bottom center",
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color='lightblue',
                size=20,
                line_width=2
            )
        )

        fig = go.Figure(data=[edge_trace, node_trace],
            layout=go.Layout(
                title='<br>Causal DAG',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[dict(
                    text="",
                    showarrow=False,
                    xref="paper",
                    yref="paper"
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )

        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        logger.debug("Plotly figure created successfully.")
        return fig

    except Exception as e:
        logger.exception(f"Error during Plotly visualization: {e}")
        return None

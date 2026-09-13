try:
    import streamlit as st # pyright: ignore[reportMissingImports]
except Exception as e:
    raise ImportError(
        "The 'streamlit' package is required to run this app. Install it with 'pip install streamlit'."
    ) from e
import pandas as pd # pyright: ignore[reportMissingModuleSource]
import networkx as nx # pyright: ignore[reportMissingModuleSource]
import plotly.graph_objects as go # pyright: ignore[reportMissingImports]
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Bitcoin Traffic Monitor",
    page_icon="₿",
    layout="wide"
)


# =========================================================
# LOAD FILE
# =========================================================

@st.cache_data
def load_csv(filename):

    path = PROCESSED_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


alerts = load_csv("prioritized_alerts.csv")
wallets = load_csv("wallet_risk_scores.csv")
ips = load_csv("ip_risk_scores.csv")
transactions = load_csv("transaction_risk_scores.csv")
correlation = load_csv("ip_txid_wallet_correlation.csv")

clusters = load_csv("wallet_clusters.csv")
cluster_stats = load_csv("cluster_statistics.csv")
metrics = load_csv("ml_evaluation_metrics.csv")


# =========================================================
# TITLE
# =========================================================

st.title("₿ AI-Powered Bitcoin Transaction Monitor")

st.caption(
    "Offline blockchain and network anomaly-analysis platform"
)


if alerts.empty:

    st.error(
        "No alert data found. Run the ML and risk-scoring pipeline first."
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Investigation Controls")

risk_options = [
    "ALL",
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW"
]

selected_risk = st.sidebar.selectbox(
    "Risk Level",
    risk_options
)

entity_options = [
    "ALL",
    "WALLET",
    "IP",
    "TRANSACTION"
]

selected_type = st.sidebar.selectbox(
    "Entity Type",
    entity_options
)


# =========================================================
# FILTER ALERTS
# =========================================================

filtered_alerts = alerts.copy()

if selected_risk != "ALL":

    filtered_alerts = filtered_alerts[
        filtered_alerts["risk_level"]
        == selected_risk
    ]

if selected_type != "ALL":

    filtered_alerts = filtered_alerts[
        filtered_alerts["entity_type"]
        == selected_type
    ]


# =========================================================
# OVERVIEW METRICS
# =========================================================

total_transactions = len(transactions)

total_wallets = len(wallets)

total_ips = len(ips)

total_alerts = len(alerts)

critical = (
    alerts["risk_level"]
    .eq("CRITICAL")
    .sum()
)

high = (
    alerts["risk_level"]
    .eq("HIGH")
    .sum()
)


c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Transactions",
    f"{total_transactions:,}"
)

c2.metric(
    "Wallets",
    f"{total_wallets:,}"
)

c3.metric(
    "IPs",
    f"{total_ips:,}"
)

c4.metric(
    "Alerts",
    f"{total_alerts:,}"
)

c5.metric(
    "Critical + High",
    f"{critical + high:,}"
)


# =========================================================
# RISK DISTRIBUTION
# =========================================================

st.subheader("Risk Distribution")

risk_counts = (
    alerts["risk_level"]
    .value_counts()
    .reindex(
        [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ],
        fill_value=0
    )
)

risk_fig = go.Figure()

risk_fig.add_trace(
    go.Bar(
        x=risk_counts.index,
        y=risk_counts.values,
        text=risk_counts.values,
        textposition="auto"
    )
)

risk_fig.update_layout(
    height=350,
    xaxis_title="Risk Level",
    yaxis_title="Number of Alerts"
)

st.plotly_chart(
    risk_fig,
    use_container_width=True
)


# =========================================================
# ALERT TABLE
# =========================================================

st.subheader(
    "Prioritized Investigative Leads"
)

alert_columns = [
    "priority_rank",
    "entity_type",
    "entity",
    "risk_score",
    "risk_level",
    "confidence"
]

available_columns = [
    c
    for c in alert_columns
    if c in filtered_alerts.columns
]

st.dataframe(
    filtered_alerts[
        available_columns
    ].head(100),
    use_container_width=True,
    hide_index=True
)

# =========================================================
# ENTITY CLUSTERING
# =========================================================

st.subheader("Entity Clustering")

if not clusters.empty:

    # Number of actual clusters
    total_clusters = (
        clusters.loc[
            clusters["cluster_id"] != -1,
            "cluster_id"
        ]
        .nunique()
    )

    # Number of DBSCAN noise entities
    noise_entities = (
        clusters["cluster_id"] == -1
    ).sum()

    # Number of clustered wallets
    clustered_entities = (
        clusters["cluster_id"] != -1
    ).sum()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Behavioral Clusters",
        int(total_clusters)
    )

    c2.metric(
        "Clustered Wallets",
        int(clustered_entities)
    )

    c3.metric(
        "Noise Wallets",
        int(noise_entities)
    )

    st.write(
        "DBSCAN groups wallets according to behavioral "
        "similarity. Noise entities do not fit a sufficiently "
        "dense cluster under the selected DBSCAN parameters."
    )

    display_columns = [
        "wallet",
        "cluster_id",
        "cluster_type",
        "risk_score"
    ]

    display_columns = [
        column
        for column in display_columns
        if column in clusters.columns
    ]

    st.dataframe(
        clusters[
            display_columns
        ]
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(100),
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "wallet_clusters.csv was not found."
    )

if not cluster_stats.empty:

    st.write("### Cluster Statistics")

    st.dataframe(
        cluster_stats,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# ENTITY SELECTION
# =========================================================

st.subheader(
    "Investigate Entity"
)

entities = (
    filtered_alerts["entity"]
    .dropna()
    .astype(str)
    .tolist()
)

if not entities:

    st.warning(
        "No entities match the selected filters."
    )

    st.stop()

selected_entity = st.selectbox(
    "Select an entity",
    entities
)


selected_rows = alerts[
    alerts["entity"]
    .astype(str)
    == selected_entity
]


if selected_rows.empty:

    st.warning(
        "Entity information not found."
    )

    st.stop()


selected = selected_rows.iloc[0]


# =========================================================
# ENTITY SUMMARY
# =========================================================

e1, e2, e3, e4 = st.columns(4)

e1.metric(
    "Entity Type",
    selected["entity_type"]
)

e2.metric(
    "Risk Score",
    f"{selected['risk_score']:.2f}"
)

e3.metric(
    "Risk Level",
    selected["risk_level"]
)

e4.metric(
    "Confidence",
    f"{selected['confidence']:.2f}"
)


# =========================================================
# EXPLANATION
# =========================================================

st.subheader(
    "Why Was This Entity Flagged?"
)

st.info(
    selected["evidence"]
)


# =========================================================
# ENTITY DETAILS
# =========================================================

st.subheader(
    "Entity Details"
)


entity_type = selected["entity_type"]


if entity_type == "WALLET":

    wallet_match = wallets[
        wallets["wallet"].astype(str)
        == selected_entity
    ]

    if not wallet_match.empty:

        st.dataframe(
            wallet_match,
            use_container_width=True,
            hide_index=True
        )


elif entity_type == "IP":

    ip_match = ips[
        ips["src_ip"].astype(str)
        == selected_entity
    ]

    if not ip_match.empty:

        st.dataframe(
            ip_match,
            use_container_width=True,
            hide_index=True
        )


elif entity_type == "TRANSACTION":

    tx_match = transactions[
        transactions["txid"].astype(str)
        == selected_entity
    ]

    if not tx_match.empty:

        st.dataframe(
            tx_match,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# RELATED TRANSACTIONS
# =========================================================

st.subheader(
    "Related Transactions"
)


if not correlation.empty:

    related = correlation[
        (
            correlation["src_ip"]
            .astype(str)
            .eq(selected_entity)
        )
        |
        (
            correlation["input_wallet"]
            .astype(str)
            .eq(selected_entity)
        )
        |
        (
            correlation["output_wallet"]
            .astype(str)
            .eq(selected_entity)
        )
        |
        (
            correlation["txid"]
            .astype(str)
            .eq(selected_entity)
        )
    ]

    if not related.empty:

        related_columns = [
            "timestamp",
            "src_ip",
            "dst_ip",
            "txid",
            "input_wallet",
            "output_wallet",
            "transaction_amount",
            "fee",
            "geo_country",
            "asn"
        ]

        related_columns = [
            c
            for c in related_columns
            if c in related.columns
        ]

        st.dataframe(
            related[
                related_columns
            ].head(100),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No related transactions found."
        )


# =========================================================
# LINK ANALYSIS
# =========================================================

st.subheader(
    "Link Analysis"
)


def build_graph(entity, df):

    graph = nx.Graph()

    matching = df[
        (
            df["src_ip"]
            .astype(str)
            .eq(entity)
        )
        |
        (
            df["input_wallet"]
            .astype(str)
            .eq(entity)
        )
        |
        (
            df["output_wallet"]
            .astype(str)
            .eq(entity)
        )
        |
        (
            df["txid"]
            .astype(str)
            .eq(entity)
        )
    ]

    # Keep the visualization manageable
    matching = matching.head(100)

    for _, row in matching.iterrows():

        ip = str(row["src_ip"])
        tx = str(row["txid"])
        input_wallet = str(row["input_wallet"])
        output_wallet = str(row["output_wallet"])

        graph.add_node(
            ip,
            node_type="IP"
        )

        graph.add_node(
            tx,
            node_type="TRANSACTION"
        )

        graph.add_node(
            input_wallet,
            node_type="WALLET"
        )

        graph.add_node(
            output_wallet,
            node_type="WALLET"
        )

        graph.add_edge(
            ip,
            tx
        )

        graph.add_edge(
            tx,
            input_wallet
        )

        graph.add_edge(
            tx,
            output_wallet
        )

    return graph


if not correlation.empty:

    graph = build_graph(
        selected_entity,
        correlation
    )

    if graph.number_of_nodes() > 0:

        positions = nx.spring_layout(
            graph,
            seed=42
        )

        # -------------------------------------------------
        # Edges
        # -------------------------------------------------

        edge_x = []
        edge_y = []

        for source, target in graph.edges():

            x0, y0 = positions[source]

            x1, y1 = positions[target]

            edge_x.extend(
                [x0, x1, None]
            )

            edge_y.extend(
                [y0, y1, None]
            )

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            hoverinfo="none"
        )

        # -------------------------------------------------
        # Nodes
        # -------------------------------------------------

        node_x = []
        node_y = []
        node_text = []

        for node in graph.nodes():

            x, y = positions[node]

            node_x.append(x)
            node_y.append(y)

            node_type = (
                graph.nodes[node]
                .get(
                    "node_type",
                    "UNKNOWN"
                )
            )

            node_text.append(
                f"{node}<br>"
                f"Type: {node_type}<br>"
                f"Degree: {graph.degree[node]}"
            )

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=list(graph.nodes()),
            textposition="top center",
            hovertext=node_text,
            hoverinfo="text",
            marker=dict(
                size=18
            )
        )

        graph_fig = go.Figure(
            data=[
                edge_trace,
                node_trace
            ]
        )

        graph_fig.update_layout(
            height=650,
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            )
        )

        st.plotly_chart(
            graph_fig,
            use_container_width=True
        )

    else:

        st.info(
            "No graph relationships found."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Synthetic dataset | Offline analysis | "
    "AI/ML anomaly detection | "
    "Risk scores are investigative prioritization signals, "
    "not determinations of criminal activity."
)
# =========================================================
# ML MODEL PERFORMANCE
# =========================================================

st.subheader("ML Model Performance")

if not metrics.empty:

    precision = pd.to_numeric(
        metrics.iloc[0]["precision"],
        errors="coerce"
    )

    recall = pd.to_numeric(
        metrics.iloc[0]["recall"],
        errors="coerce"
    )

    f1_score = pd.to_numeric(
        metrics.iloc[0]["f1_score"],
        errors="coerce"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Precision",
        f"{precision:.2%}"
    )

    c2.metric(
        "Recall",
        f"{recall:.2%}"
    )

    c3.metric(
        "F1 Score",
        f"{f1_score:.2%}"
    )

else:

    st.warning(
        "ML evaluation results are not available."
    )
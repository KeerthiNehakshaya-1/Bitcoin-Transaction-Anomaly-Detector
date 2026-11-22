import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path
import ast
import json
import re


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Entity Graph",
    page_icon="🕸️",
    layout="wide"
)

st.title("🕸️ Entity Graph")

st.write(
    "Interactive investigation of relationships between "
    "IP addresses, transactions, and wallet addresses."
)


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# DATA FILES
# =========================================================

ENRICHED_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "bitcoin_transactions_enriched.csv"
)

CLEANED_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "bitcoin_transactions_cleaned.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    if ENRICHED_FILE.exists():

        dataframe = pd.read_csv(
            ENRICHED_FILE
        )

        return dataframe, ENRICHED_FILE

    if CLEANED_FILE.exists():

        dataframe = pd.read_csv(
            CLEANED_FILE
        )

        return dataframe, CLEANED_FILE

    return None, None


df, source_file = load_data()


# =========================================================
# DATA CHECK
# =========================================================

if df is None:

    st.error(
        "Processed transaction data was not found.\n\n"
        "Expected one of these files:\n\n"
        "data/processed/bitcoin_transactions_enriched.csv\n"
        "data/processed/bitcoin_transactions_cleaned.csv"
    )

    st.stop()


# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = [
    str(column).strip()
    for column in df.columns
]


st.caption(
    f"Graph source: `{source_file.name}`"
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_column(dataframe, names):

    for name in names:

        if name in dataframe.columns:
            return name

    return None


def parse_list(value):

    """
    Convert list-like values from CSV into Python list.
    """

    if pd.isna(value):
        return []

    if isinstance(value, list):

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    value = str(value).strip()

    if not value:
        return []

    # -----------------------------------------------------
    # JSON list
    # -----------------------------------------------------

    try:

        result = json.loads(value)

        if isinstance(result, list):

            return [
                str(item).strip()
                for item in result
                if str(item).strip()
            ]

    except Exception:
        pass

    # -----------------------------------------------------
    # Python list
    # -----------------------------------------------------

    try:

        result = ast.literal_eval(value)

        if isinstance(result, list):

            return [
                str(item).strip()
                for item in result
                if str(item).strip()
            ]

    except Exception:
        pass

    # -----------------------------------------------------
    # Comma-separated values
    # -----------------------------------------------------

    cleaned = (
        value
        .replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace('"', "")
    )

    return [
        item.strip()
        for item in cleaned.split(",")
        if item.strip()
    ]


def transaction_numeric_part(txid):

    match = re.search(
        r"(\d+)$",
        str(txid).strip()
    )

    if match:
        return match.group(1)

    return ""


def format_txid(txid):

    number = transaction_numeric_part(
        txid
    )

    if number:
        return f"{txid} | {number}"

    return str(txid)


# =========================================================
# IDENTIFY COLUMNS
# =========================================================

TXID_COLUMN = get_column(
    df,
    [
        "txid",
        "transaction_id",
        "TXID"
    ]
)

SRC_IP_COLUMN = get_column(
    df,
    [
        "src_ip",
        "source_ip"
    ]
)

DST_IP_COLUMN = get_column(
    df,
    [
        "dst_ip",
        "destination_ip"
    ]
)

INPUT_WALLET_COLUMN = get_column(
    df,
    [
        "input_addresses",
        "input_wallets",
        "input_wallet"
    ]
)

OUTPUT_WALLET_COLUMN = get_column(
    df,
    [
        "output_addresses",
        "output_wallets",
        "output_wallet"
    ]
)


# =========================================================
# REQUIRED COLUMN CHECK
# =========================================================

missing_columns = []

if TXID_COLUMN is None:
    missing_columns.append("txid")

if SRC_IP_COLUMN is None:
    missing_columns.append("src_ip")

if DST_IP_COLUMN is None:
    missing_columns.append("dst_ip")

if (
    INPUT_WALLET_COLUMN is None
    and OUTPUT_WALLET_COLUMN is None
):
    missing_columns.append(
        "input_addresses / output_addresses"
    )


if missing_columns:

    st.error(
        "Required graph columns are missing:\n\n"
        + "\n".join(
            f"• {column}"
            for column in missing_columns
        )
    )

    st.write(
        "Available columns:"
    )

    st.write(
        list(df.columns)
    )

    st.stop()


# =========================================================
# BUILD ENTITY LISTS
# =========================================================

@st.cache_data
def build_entity_lists(dataframe):

    ip_set = set()
    tx_set = set()
    wallet_set = set()

    # -----------------------------------------------------
    # IP addresses
    # -----------------------------------------------------

    for column in [
        SRC_IP_COLUMN,
        DST_IP_COLUMN
    ]:

        if column is None:
            continue

        for value in (
            dataframe[column]
            .dropna()
            .astype(str)
        ):

            value = value.strip()

            if value:
                ip_set.add(value)

    # -----------------------------------------------------
    # Transaction IDs
    # -----------------------------------------------------

    for value in (
        dataframe[TXID_COLUMN]
        .dropna()
        .astype(str)
    ):

        value = value.strip()

        if value:
            tx_set.add(value)

    # -----------------------------------------------------
    # Wallets
    # -----------------------------------------------------

    for column in [
        INPUT_WALLET_COLUMN,
        OUTPUT_WALLET_COLUMN
    ]:

        if column is None:
            continue

        for value in dataframe[column].dropna():

            wallets = parse_list(value)

            for wallet in wallets:

                wallet = str(wallet).strip()

                if wallet:
                    wallet_set.add(wallet)

    return (
        sorted(ip_set),
        sorted(tx_set),
        sorted(wallet_set)
    )


(
    ip_values,
    txid_values,
    wallet_values
) = build_entity_lists(df)


# =========================================================
# BUILD COMPLETE GRAPH
# =========================================================

@st.cache_resource
def build_graph(dataframe):

    graph = nx.Graph()

    for _, row in dataframe.iterrows():

        # =================================================
        # TRANSACTION NODE
        # =================================================

        txid = str(
            row[TXID_COLUMN]
        ).strip()

        if not txid:
            continue

        transaction_node = (
            f"TRANSACTION::{txid}"
        )

        graph.add_node(
            transaction_node,
            entity_type="TRANSACTION",
            label=txid
        )

        # =================================================
        # SOURCE IP
        # =================================================

        if SRC_IP_COLUMN:

            src_ip = str(
                row[SRC_IP_COLUMN]
            ).strip()

            if (
                src_ip
                and src_ip != "nan"
            ):

                ip_node = (
                    f"IP::{src_ip}"
                )

                graph.add_node(
                    ip_node,
                    entity_type="IP",
                    label=src_ip
                )

                graph.add_edge(
                    ip_node,
                    transaction_node,
                    relationship="OBSERVED"
                )

        # =================================================
        # DESTINATION IP
        # =================================================

        if DST_IP_COLUMN:

            dst_ip = str(
                row[DST_IP_COLUMN]
            ).strip()

            if (
                dst_ip
                and dst_ip != "nan"
            ):

                ip_node = (
                    f"IP::{dst_ip}"
                )

                graph.add_node(
                    ip_node,
                    entity_type="IP",
                    label=dst_ip
                )

                graph.add_edge(
                    ip_node,
                    transaction_node,
                    relationship="DESTINATION"
                )

        # =================================================
        # INPUT WALLETS
        # =================================================

        if INPUT_WALLET_COLUMN:

            input_wallets = parse_list(
                row[INPUT_WALLET_COLUMN]
            )

            for wallet in input_wallets:

                wallet = str(
                    wallet
                ).strip()

                if not wallet:
                    continue

                wallet_node = (
                    f"WALLET::{wallet}"
                )

                graph.add_node(
                    wallet_node,
                    entity_type="WALLET",
                    label=wallet
                )

                graph.add_edge(
                    transaction_node,
                    wallet_node,
                    relationship="INPUT"
                )

        # =================================================
        # OUTPUT WALLETS
        # =================================================

        if OUTPUT_WALLET_COLUMN:

            output_wallets = parse_list(
                row[OUTPUT_WALLET_COLUMN]
            )

            for wallet in output_wallets:

                wallet = str(
                    wallet
                ).strip()

                if not wallet:
                    continue

                wallet_node = (
                    f"WALLET::{wallet}"
                )

                graph.add_node(
                    wallet_node,
                    entity_type="WALLET",
                    label=wallet
                )

                graph.add_edge(
                    transaction_node,
                    wallet_node,
                    relationship="OUTPUT"
                )

    return graph


G = build_graph(df)


# =========================================================
# SESSION STATE
# =========================================================

if "root_entity" not in st.session_state:
    st.session_state.root_entity = None

if "root_type" not in st.session_state:
    st.session_state.root_type = None

if "current_entity" not in st.session_state:
    st.session_state.current_entity = None

if "current_type" not in st.session_state:
    st.session_state.current_type = None

if "exploration_history" not in st.session_state:
    st.session_state.exploration_history = []

if "pending_node" not in st.session_state:
    st.session_state.pending_node = None

if "focus_mode" not in st.session_state:
    st.session_state.focus_mode = False

if "focus_node" not in st.session_state:
    st.session_state.focus_node = None

if "search_entity" not in st.session_state:
    st.session_state.search_entity = None

if "search_type" not in st.session_state:
    st.session_state.search_type = None

if "max_nodes_context" not in st.session_state:
    st.session_state.max_nodes_context = None

if "max_nodes_value" not in st.session_state:
    st.session_state.max_nodes_value = 1


# =========================================================
# GRAPH SUMMARY
# =========================================================

st.subheader(
    "📊 Graph Summary"
)

summary1, summary2, summary3, summary4 = (
    st.columns(4)
)

with summary1:

    st.metric(
        "IP Entities",
        f"{len(ip_values):,}"
    )

with summary2:

    st.metric(
        "Transaction Entities",
        f"{len(txid_values):,}"
    )

with summary3:

    st.metric(
        "Wallet Entities",
        f"{len(wallet_values):,}"
    )

with summary4:

    st.metric(
        "Total Graph Nodes",
        f"{G.number_of_nodes():,}"
    )


st.divider()


# =========================================================
# SEARCH ENTITY
# =========================================================

st.subheader(
    "🔎 Select Investigation Entity"
)

entity_type = st.radio(
    "Entity Type",
    [
        "IP Address",
        "Transaction ID",
        "Wallet Address"
    ],
    horizontal=True
)


# =========================================================
# IP SEARCH
# =========================================================

if entity_type == "IP Address":

    if not ip_values:

        st.warning(
            "No IP addresses were found."
        )

        st.stop()

    searched_entity = st.selectbox(
        "Search IP Address",
        [""] + ip_values,
        index=0,
        help=(
            "Type part of the IP address "
            "to filter suggestions."
        )
    )

    searched_type = "IP"


# =========================================================
# TRANSACTION SEARCH
# =========================================================

elif entity_type == "Transaction ID":

    if not txid_values:

        st.warning(
            "No transaction IDs were found."
        )

        st.stop()

    searched_entity = st.selectbox(
        "Search Transaction ID",
        [""] + txid_values,
        index=0,
        format_func=lambda value: (
            "Select Transaction ID..."
            if value == ""
            else format_txid(value)
        ),
        help=(
            "Type part of the transaction ID "
            "or its numeric portion."
        )
    )

    searched_type = "TRANSACTION"


# =========================================================
# WALLET SEARCH
# =========================================================

else:

    if not wallet_values:

        st.warning(
            "No wallet addresses were found."
        )

        st.stop()

    searched_entity = st.selectbox(
        "Search Wallet Address",
        [""] + wallet_values,
        index=0,
        help=(
            "Type part of the wallet address "
            "to filter suggestions."
        )
    )

    searched_type = "WALLET"


# =========================================================
# HANDLE NEW SEARCH
# =========================================================

if searched_entity:

    new_search = (
        st.session_state.search_entity
        != searched_entity
        or
        st.session_state.search_type
        != searched_type
    )

    if new_search:

        # -------------------------------------------------
        # Original investigation anchor
        # -------------------------------------------------

        st.session_state.root_entity = (
            searched_entity
        )

        st.session_state.root_type = (
            searched_type
        )

        # -------------------------------------------------
        # Current exploration center
        # -------------------------------------------------

        st.session_state.current_entity = (
            searched_entity
        )

        st.session_state.current_type = (
            searched_type
        )

        # -------------------------------------------------
        # Clear old state
        # -------------------------------------------------

        st.session_state.exploration_history = []

        st.session_state.pending_node = None

        st.session_state.focus_mode = False

        st.session_state.focus_node = None

        # -------------------------------------------------
        # Save search
        # -------------------------------------------------

        st.session_state.search_entity = (
            searched_entity
        )

        st.session_state.search_type = (
            searched_type
        )

        # -------------------------------------------------
        # Force maximum nodes to reset
        # -------------------------------------------------

        st.session_state.max_nodes_context = None


# =========================================================
# CHECK WHETHER INVESTIGATION EXISTS
# =========================================================

if (
    st.session_state.root_entity
    is None
):

    st.info(
        "Select an IP Address, Transaction ID, "
        "or Wallet Address to start the investigation."
    )

    st.stop()


# =========================================================
# ROOT INVESTIGATION
# =========================================================

root_entity = (
    st.session_state.root_entity
)

root_type = (
    st.session_state.root_type
)

root_node = (
    f"{root_type}::{root_entity}"
)


# =========================================================
# CURRENT EXPLORATION CENTER
# =========================================================

current_entity = (
    st.session_state.current_entity
)

current_type = (
    st.session_state.current_type
)

current_node = (
    f"{current_type}::{current_entity}"
)


# =========================================================
# VERIFY CURRENT NODE
# =========================================================

if current_node not in G:

    st.error(
        "The current investigation entity "
        "is not present in the graph."
    )

    st.stop()


# =========================================================
# INVESTIGATION INFORMATION
# =========================================================

st.divider()

st.subheader(
    "🎯 Investigation Context"
)

context1, context2, context3 = (
    st.columns(3)
)

with context1:

    st.write(
        f"**Original Entity:** "
        f"`{root_entity}`"
    )

with context2:

    st.write(
        f"**Original Type:** "
        f"{root_type}"
    )

with context3:

    st.write(
        f"**Current Center:** "
        f"`{current_entity}`"
    )


# =========================================================
# CONNECTION DEPTH
# =========================================================

st.subheader(
    "⚙️ Graph Settings"
)

connection_depth = st.selectbox(
    "Connection Depth",
    [
        1,
        2,
        3,
        "All Connections"
    ],
    index=0,
    format_func=lambda value: (
        "1 Level"
        if value == 1
        else (
            "2 Levels"
            if value == 2
            else (
                "3 Levels"
                if value == 3
                else "All Connections"
            )
        )
    ),
    help=(
        "1 Level = directly connected nodes.\n"
        "2 Levels = nodes up to two relationship steps away.\n"
        "3 Levels = nodes up to three relationship steps away.\n"
        "All Connections = every node reachable from the current center."
    )
)


# =========================================================
# FIND ROOT INVESTIGATION NETWORK
# =========================================================

if connection_depth == "All Connections":

    root_distances = (
        nx.single_source_shortest_path_length(
            G,
            root_node
        )
    )

else:

    root_distances = (
        nx.single_source_shortest_path_length(
            G,
            root_node,
            cutoff=connection_depth
        )
    )


root_context_nodes = set(
    root_distances.keys()
)


# =========================================================
# FIND CURRENT CENTER NETWORK
# =========================================================

if connection_depth == "All Connections":

    current_distances = (
        nx.single_source_shortest_path_length(
            G,
            current_node
        )
    )

else:

    current_distances = (
        nx.single_source_shortest_path_length(
            G,
            current_node,
            cutoff=connection_depth
        )
    )


current_context_nodes = set(
    current_distances.keys()
)


# =========================================================
# DETERMINE AVAILABLE NODES
# =========================================================

if (
    st.session_state.focus_mode
    and
    st.session_state.focus_node is not None
):

    # =====================================================
    # FOCUS MODE
    # =====================================================

    clicked_node = (
        st.session_state.focus_node
    )


    # -----------------------------------------------------
    # Find every direct connection of clicked node
    # -----------------------------------------------------

    clicked_neighbors = set(
        G.neighbors(
            clicked_node
        )
    )


    # -----------------------------------------------------
    # Restrict those connections to the ORIGINAL
    # investigation network.
    # -----------------------------------------------------

    valid_focus_neighbors = (
        clicked_neighbors
        & root_context_nodes
    )


    # -----------------------------------------------------
    # Focus view:
    #
    # clicked node
    # +
    # all its direct links within original investigation
    # -----------------------------------------------------

    focus_available_nodes = (
        [clicked_node]
        + sorted(
            valid_focus_neighbors
        )
    )


    # Remove duplicates
    focus_available_nodes = list(
        dict.fromkeys(
            focus_available_nodes
        )
    )


    available_nodes_for_view = (
        focus_available_nodes
    )


    total_available_nodes = (
        len(
            available_nodes_for_view
        )
    )


else:

    # =====================================================
    # NORMAL / EXPLORE MODE
    # =====================================================

    available_nodes_for_view = list(
        current_context_nodes
    )


    total_available_nodes = (
        len(
            available_nodes_for_view
        )
    )


# =========================================================
# MAXIMUM NODE RESET LOGIC
# =========================================================

graph_context_signature = (
    f"root={root_type}:{root_entity}|"
    f"current={current_type}:{current_entity}|"
    f"depth={connection_depth}|"
    f"focus_mode={st.session_state.focus_mode}|"
    f"focus_node={st.session_state.focus_node}|"
    f"available={total_available_nodes}"
)


# ---------------------------------------------------------
# Every time the graph context changes, reset Maximum
# Graph Nodes to the new actual maximum.
# ---------------------------------------------------------

if (
    st.session_state.max_nodes_context
    != graph_context_signature
):

    st.session_state.max_nodes_context = (
        graph_context_signature
    )

    st.session_state.max_nodes_value = max(
        1,
        total_available_nodes
    )


# ---------------------------------------------------------
# Safety check
# ---------------------------------------------------------

if (
    st.session_state.max_nodes_value
    > total_available_nodes
):

    st.session_state.max_nodes_value = max(
        1,
        total_available_nodes
    )


# =========================================================
# MAXIMUM GRAPH NODES
# =========================================================

st.subheader(
    "📌 Graph Node Range"
)

max_nodes = st.number_input(
    "Maximum Graph Nodes",
    min_value=1,
    max_value=max(
        1,
        total_available_nodes
    ),
    value=max(
        1,
        st.session_state.max_nodes_value
    ),
    step=1,
    key="max_nodes_value",
    help=(
        "Automatically starts at the total number of "
        "available nodes for the current graph view."
    )
)


st.caption(
    f"Maximum possible for current view: "
    f"**{total_available_nodes:,}**"
)


st.caption(
    f"Total nodes in complete graph: "
    f"**{G.number_of_nodes():,}**"
)


# =========================================================
# CREATE DISPLAY NODE LIST
# =========================================================

if (
    st.session_state.focus_mode
    and
    st.session_state.focus_node is not None
):

    # =====================================================
    # FOCUS MODE
    # =====================================================

    clicked_node = (
        st.session_state.focus_node
    )


    focus_candidates = [
        node
        for node in available_nodes_for_view
        if node != clicked_node
    ]


    # Clicked node always stays first.

    selected_nodes = (
        [clicked_node]
        + focus_candidates[
            :int(max_nodes) - 1
        ]
    )


    display_center_node = (
        clicked_node
    )

else:

    # =====================================================
    # NORMAL / EXPLORE MODE
    # =====================================================

    candidate_nodes = [
        node
        for node in available_nodes_for_view
        if node != current_node
    ]


    # Closest nodes first.
    # Degree is used only to break ties.

    candidate_nodes.sort(
        key=lambda node: (
            current_distances.get(
                node,
                999999
            ),
            -G.degree(node)
        )
    )


    selected_nodes = (
        [current_node]
        + candidate_nodes[
            :int(max_nodes) - 1
        ]
    )


    display_center_node = (
        current_node
    )


# =========================================================
# BUILD DISPLAY SUBGRAPH
# =========================================================

subgraph = G.subgraph(
    selected_nodes
).copy()


# =========================================================
# MODE STATUS
# =========================================================

if st.session_state.focus_mode:

    focused_data = G.nodes[
        display_center_node
    ]


    focused_label = (
        focused_data.get(
            "label",
            display_center_node
        )
    )


    focused_type = (
        focused_data.get(
            "entity_type",
            "UNKNOWN"
        )
    )


    st.info(
        f"🎯 **Focus Mode**\n\n"
        f"Clicked entity: `{focused_label}` "
        f"({focused_type})\n\n"
        f"Original investigation: "
        f"`{root_entity}`\n\n"
        f"Showing the clicked node and its direct "
        f"connections that belong to the original "
        f"investigation."
    )


    if st.button(
        "↩️ Return to Investigation Graph",
        use_container_width=False
    ):

        st.session_state.focus_mode = False

        st.session_state.focus_node = None

        st.session_state.max_nodes_context = None

        st.rerun()


else:

    if max_nodes < total_available_nodes:

        st.warning(
            f"Displaying {len(subgraph.nodes):,} of "
            f"{total_available_nodes:,} available nodes. "
            f"The remaining nodes are hidden only because "
            f"of the Maximum Graph Nodes setting."
        )

    else:

        st.success(
            f"Displaying all "
            f"{total_available_nodes:,} available nodes."
        )


    st.info(
        "🖱️ Click any node in the graph. "
        "You will be able to either explore that node "
        "or focus on its links within the current investigation."
    )


# =========================================================
# METRICS
# =========================================================

metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


with metric1:

    display_label = G.nodes[
        display_center_node
    ].get(
        "label",
        display_center_node
    )


    st.metric(
        "Current Focus",
        display_label
    )


with metric2:

    st.metric(
        "Direct Connections",
        f"{G.degree(display_center_node):,}"
    )


with metric3:

    st.metric(
        "Available Nodes",
        f"{total_available_nodes:,}"
    )


with metric4:

    st.metric(
        "Displayed Nodes",
        f"{len(subgraph.nodes):,}"
    )


# =========================================================
# GRAPH VISUALIZATION
# =========================================================

if len(
    subgraph.nodes
) > 1:

    st.subheader(
        "🕸️ Interactive Relationship Graph"
    )


    # -----------------------------------------------------
    # Layout
    # -----------------------------------------------------

    if len(
        subgraph.nodes
    ) <= 50:

        iterations = 100

    elif len(
        subgraph.nodes
    ) <= 100:

        iterations = 60

    else:

        iterations = 30


    pos = nx.spring_layout(
        subgraph,
        seed=42,
        k=1.2,
        iterations=iterations
    )


    # =====================================================
    # EDGES
    # =====================================================

    edge_x = []
    edge_y = []


    for source, target in (
        subgraph.edges()
    ):

        x0, y0 = pos[source]

        x1, y1 = pos[target]


        edge_x.extend(
            [
                x0,
                x1,
                None
            ]
        )


        edge_y.extend(
            [
                y0,
                y1,
                None
            ]
        )


    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(
            width=1
        )
    )


    # =====================================================
    # NODES
    # =====================================================

    node_x = []
    node_y = []

    node_text = []
    node_hover = []
    node_customdata = []
    node_sizes = []


    for node in (
        subgraph.nodes()
    ):

        x, y = pos[node]


        node_x.append(
            x
        )

        node_y.append(
            y
        )


        node_data = (
            subgraph.nodes[node]
        )


        label = node_data.get(
            "label",
            node
        )


        entity_kind = node_data.get(
            "entity_type",
            "UNKNOWN"
        )


        node_text.append(
            label
        )


        node_hover.append(
            f"Type: {entity_kind}<br>"
            f"Entity: {label}<br>"
            f"Total Connections: "
            f"{G.degree(node)}<br>"
            f"<b>Click this node</b>"
        )


        node_customdata.append(
            node
        )


        # Current graph center is larger.

        if node == display_center_node:

            node_sizes.append(
                34
            )

        else:

            node_sizes.append(
                18
            )


    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hovertext=node_hover,
        hoverinfo="text",
        customdata=node_customdata,
        marker=dict(
            size=node_sizes,
            line=dict(
                width=1
            )
        )
    )


    # =====================================================
    # FIGURE
    # =====================================================

    fig = go.Figure(
        data=[
            edge_trace,
            node_trace
        ]
    )


    fig.update_layout(
        title=(
            f"Investigation Center: "
            f"{display_label}"
        ),
        height=750,
        showlegend=False,
        hovermode="closest",
        clickmode="event+select",
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20
        ),
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


    # =====================================================
    # CLICKABLE PLOT
    # =====================================================

    plot_event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=(
            "entity_graph_focus"
            if st.session_state.focus_mode
            else "entity_graph_normal"
        ),
        on_select="rerun",
        selection_mode="points"
    )


    # =====================================================
    # HANDLE NODE CLICK
    # =====================================================

    if plot_event:

        try:

            points = (
                plot_event
                .selection
                .points
            )

        except Exception:

            points = []


        if points:

            clicked_point = (
                points[0]
            )


            clicked_node = (
                clicked_point.get(
                    "customdata"
                )
            )


            if clicked_node:

                if (
                    clicked_node
                    != display_center_node
                ):

                    clicked_data = G.nodes[
                        clicked_node
                    ]


                    clicked_label = (
                        clicked_data.get(
                            "label",
                            clicked_node
                        )
                    )


                    clicked_type = (
                        clicked_data.get(
                            "entity_type",
                            "UNKNOWN"
                        )
                    )


                    # Store clicked node.

                    st.session_state.pending_node = {
                        "node": clicked_node,
                        "label": clicked_label,
                        "type": clicked_type
                    }


                    st.rerun()


else:

    st.info(
        "No connected entities are available "
        "in the current view."
    )


# =========================================================
# CLICKED NODE OPTIONS
# =========================================================

if st.session_state.pending_node:

    pending = (
        st.session_state.pending_node
    )


    clicked_node = (
        pending["node"]
    )


    clicked_label = (
        pending["label"]
    )


    clicked_type = (
        pending["type"]
    )


    st.divider()


    st.subheader(
        "🖱️ Node Selected"
    )


    st.write(
        f"**Entity Type:** {clicked_type}"
    )


    st.write(
        f"**Entity:** `{clicked_label}`"
    )


    st.info(
        "Choose what you want to do with this node."
    )


    option1, option2 = (
        st.columns(2)
    )


    # =====================================================
    # OPTION 1: EXPLORE NODE
    # =====================================================

    with option1:

        if st.button(
            "🔎 Explore This Node",
            use_container_width=True
        ):

            # Save current center.

            st.session_state.exploration_history.append(
                (
                    current_entity,
                    current_type
                )
            )


            # Clicked node becomes current center.

            st.session_state.current_entity = (
                clicked_label
            )


            st.session_state.current_type = (
                clicked_type
            )


            # Leave focus mode.

            st.session_state.focus_mode = False

            st.session_state.focus_node = None


            # Clear click.

            st.session_state.pending_node = None


            # Reset maximum to the new graph's total.

            st.session_state.max_nodes_context = None


            st.rerun()


    # =====================================================
    # OPTION 2: FOCUS ON NODE LINKS
    # =====================================================

    with option2:

        if st.button(
            "🎯 Focus on This Node's Links",
            use_container_width=True
        ):

            # Keep original investigation unchanged.

            st.session_state.focus_mode = True

            st.session_state.focus_node = clicked_node


            # Clear click.

            st.session_state.pending_node = None


            # Reset maximum to the number of links
            # available in this new focused view.

            st.session_state.max_nodes_context = None


            st.rerun()


# =========================================================
# NAVIGATION
# =========================================================

st.divider()

st.subheader(
    "↩️ Investigation Navigation"
)


nav1, nav2, nav3 = (
    st.columns(3)
)


# =========================================================
# PREVIOUS ENTITY
# =========================================================

with nav1:

    if st.session_state.exploration_history:

        if st.button(
            "⬅️ Previous Entity",
            use_container_width=True
        ):

            previous_entity, previous_type = (
                st.session_state.exploration_history.pop()
            )


            st.session_state.current_entity = (
                previous_entity
            )


            st.session_state.current_type = (
                previous_type
            )


            st.session_state.focus_mode = False

            st.session_state.focus_node = None

            st.session_state.pending_node = None

            st.session_state.max_nodes_context = None

            st.rerun()

    else:

        st.caption(
            "No previous entity."
        )


# =========================================================
# ORIGINAL INVESTIGATION
# =========================================================

with nav2:

    if st.button(
        "🏠 Original Investigation",
        use_container_width=True
    ):

        st.session_state.current_entity = (
            st.session_state.root_entity
        )


        st.session_state.current_type = (
            st.session_state.root_type
        )


        st.session_state.exploration_history = []

        st.session_state.focus_mode = False

        st.session_state.focus_node = None

        st.session_state.pending_node = None

        st.session_state.max_nodes_context = None

        st.rerun()


# =========================================================
# RESET
# =========================================================

with nav3:

    if st.button(
        "🔄 Reset",
        use_container_width=True
    ):

        st.session_state.root_entity = None

        st.session_state.root_type = None

        st.session_state.current_entity = None

        st.session_state.current_type = None

        st.session_state.exploration_history = []

        st.session_state.pending_node = None

        st.session_state.focus_mode = False

        st.session_state.focus_node = None

        st.session_state.search_entity = None

        st.session_state.search_type = None

        st.session_state.max_nodes_context = None

        st.session_state.max_nodes_value = 1

        st.rerun()


# =========================================================
# EXPLORATION PATH
# =========================================================

if st.session_state.exploration_history:

    st.subheader(
        "🧭 Exploration Path"
    )


    path_items = []


    # Original investigation root

    path_items.append(
        f"{root_type}: {root_entity}"
    )


    for entity, entity_type in (
        st.session_state.exploration_history
    ):

        path_items.append(
            f"{entity_type}: {entity}"
        )


    path_items.append(
        f"{current_type}: {current_entity}"
    )


    st.code(
        "  →  ".join(
            path_items
        )
    )


# =========================================================
# CONNECTED ENTITIES TABLE
# =========================================================

st.subheader(
    "🔗 Connected Entities"
)


connected_rows = []


for node in (
    subgraph.nodes()
):

    if node == display_center_node:

        continue


    node_data = (
        subgraph.nodes[node]
    )


    if st.session_state.focus_mode:

        distance = 1

    else:

        distance = (
            current_distances.get(
                node,
                ""
            )
        )


    connected_rows.append(
        {
            "Entity Type": node_data.get(
                "entity_type",
                "UNKNOWN"
            ),
            "Entity": node_data.get(
                "label",
                node
            ),
            "Distance": distance,
            "Total Connections": G.degree(
                node
            )
        }
    )


if connected_rows:

    connected_df = pd.DataFrame(
        connected_rows
    )


    connected_df = connected_df.sort_values(
        [
            "Distance",
            "Total Connections"
        ],
        ascending=[
            True,
            False
        ]
    )


    st.dataframe(
        connected_df,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No connected entities found."
    )


# =========================================================
# RELATIONSHIP TABLE
# =========================================================

st.subheader(
    "🔗 Relationships"
)


relationship_rows = []


for source, target in (
    subgraph.edges()
):

    source_data = (
        subgraph.nodes[source]
    )


    target_data = (
        subgraph.nodes[target]
    )


    edge_data = (
        G.get_edge_data(
            source,
            target
        )
    )


    relationship_name = (
        "CONNECTED"
    )


    if isinstance(
        edge_data,
        dict
    ):

        relationship_name = (
            edge_data.get(
                "relationship",
                "CONNECTED"
            )
        )


    relationship_rows.append(
        {
            "Source Type": source_data.get(
                "entity_type",
                "UNKNOWN"
            ),
            "Source": source_data.get(
                "label",
                source
            ),
            "Relationship": relationship_name,
            "Target Type": target_data.get(
                "entity_type",
                "UNKNOWN"
            ),
            "Target": target_data.get(
                "label",
                target
            )
        }
    )


if relationship_rows:

    relationship_df = pd.DataFrame(
        relationship_rows
    )


    st.dataframe(
        relationship_df,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No relationships available."
    )


# =========================================================
# INVESTIGATION INFORMATION
# =========================================================

st.subheader(
    "📋 Investigation Information"
)


info1, info2 = (
    st.columns(2)
)


with info1:

    st.write(
        f"**Original Investigation Entity:** "
        f"`{root_entity}`"
    )


    st.write(
        f"**Original Entity Type:** "
        f"{root_type}"
    )


    st.write(
        f"**Current Center:** "
        f"`{current_entity}`"
    )


with info2:

    st.write(
        f"**Connection Depth:** "
        f"{connection_depth}"
    )


    st.write(
        f"**Available Nodes:** "
        f"{total_available_nodes:,}"
    )


    st.write(
        f"**Displayed Nodes:** "
        f"{len(subgraph.nodes):,}"
    )


# =========================================================
# EXPORT
# =========================================================

if relationship_rows:

    st.subheader(
        "⬇️ Export Graph Data"
    )


    graph_csv = (
        pd.DataFrame(
            relationship_rows
        )
        .to_csv(
            index=False
        )
        .encode("utf-8")
    )


    st.download_button(
        label="Download Current Graph Relationships CSV",
        data=graph_csv,
        file_name=(
            "current_entity_graph.csv"
        ),
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "The graph represents relationships observed in the "
    "processed dataset. Graph relationships are analytical "
    "connections and do not independently establish malicious "
    "or unlawful activity."
)
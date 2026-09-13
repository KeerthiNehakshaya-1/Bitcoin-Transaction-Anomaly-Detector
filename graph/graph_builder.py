import pandas as pd  # type: ignore[reportMissingModuleSource]
import networkx as nx  # type: ignore[reportMissingModuleSource]
import json
from pathlib import Path


# ---------------------------------------------------------
# Utility function
# ---------------------------------------------------------

def parse_list(value):
    """Convert JSON text into a Python list."""

    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return [result]

    except (json.JSONDecodeError, TypeError):
        return []


# ---------------------------------------------------------
# Load correlation data
# ---------------------------------------------------------

def load_correlation_data():

    base_dir = Path(__file__).resolve().parent.parent

    file_path = (
        base_dir
        / "data"
        / "processed"
        / "ip_txid_wallet_correlation.csv"
    )

    print(f"Loading correlation data:")
    print(file_path)

    return pd.read_csv(file_path)


# ---------------------------------------------------------
# Prepare data
# ---------------------------------------------------------

def prepare_data(df):

    df = df.copy()

    list_columns = [
        "input_amounts",
        "output_amounts"
    ]

    for column in list_columns:

        if column in df.columns:

            df[column] = df[column].apply(parse_list)

    return df


# ---------------------------------------------------------
# Build heterogeneous graph
# ---------------------------------------------------------

def build_graph(df):

    print("\nBuilding entity graph...")

    graph = nx.MultiDiGraph()

    for _, row in df.iterrows():

        src_ip = row["src_ip"]
        dst_ip = row["dst_ip"]
        txid = row["txid"]

        input_wallet = row["input_wallet"]
        output_wallet = row["output_wallet"]

        amount = row["transaction_amount"]
        fee = row["fee"]
        timestamp = row["timestamp"]

        # -------------------------------------------------
        # Add IP nodes
        # -------------------------------------------------

        graph.add_node(
            src_ip,
            node_type="IP"
        )

        graph.add_node(
            dst_ip,
            node_type="IP"
        )

        # -------------------------------------------------
        # Add transaction node
        # -------------------------------------------------

        graph.add_node(
            txid,
            node_type="TRANSACTION",
            amount=amount,
            fee=fee,
            timestamp=timestamp
        )

        # -------------------------------------------------
        # Add wallet nodes
        # -------------------------------------------------

        graph.add_node(
            input_wallet,
            node_type="WALLET"
        )

        graph.add_node(
            output_wallet,
            node_type="WALLET"
        )

        # -------------------------------------------------
        # IP → Transaction
        # -------------------------------------------------

        graph.add_edge(
            src_ip,
            txid,
            relationship="OBSERVED",
            timestamp=timestamp
        )

        # -------------------------------------------------
        # Transaction → Destination IP
        # -------------------------------------------------

        graph.add_edge(
            txid,
            dst_ip,
            relationship="DESTINATION",
            timestamp=timestamp
        )

        # -------------------------------------------------
        # Input wallet → Transaction
        # -------------------------------------------------

        graph.add_edge(
            input_wallet,
            txid,
            relationship="INPUT",
            amount=amount
        )

        # -------------------------------------------------
        # Transaction → Output wallet
        # -------------------------------------------------

        graph.add_edge(
            txid,
            output_wallet,
            relationship="OUTPUT",
            amount=amount
        )

    return graph


# ---------------------------------------------------------
# Calculate graph features
# ---------------------------------------------------------

def calculate_graph_features(graph):

    print("\nCalculating graph features...")

    results = []

    for node, attributes in graph.nodes(data=True):

        node_type = attributes.get(
            "node_type",
            "UNKNOWN"
        )

        degree = graph.degree(node)

        in_degree = graph.in_degree(node)

        out_degree = graph.out_degree(node)

        results.append({
            "entity": node,
            "node_type": node_type,
            "degree": degree,
            "in_degree": in_degree,
            "out_degree": out_degree
        })

    feature_df = pd.DataFrame(results)

    return feature_df


# ---------------------------------------------------------
# Calculate centrality
# ---------------------------------------------------------

def calculate_centrality(graph):

    print("\nCalculating degree centrality...")

    centrality = nx.degree_centrality(graph)

    results = []

    for entity, score in centrality.items():

        results.append({
            "entity": entity,
            "degree_centrality": score
        })

    return pd.DataFrame(results)


# ---------------------------------------------------------
# Save graph data
# ---------------------------------------------------------

def save_graph(graph):

    base_dir = Path(__file__).resolve().parent.parent

    output_dir = (
        base_dir
        / "data"
        / "processed"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    graph_file = (
        output_dir
        / "bitcoin_entity_graph.graphml"
    )

    nx.write_graphml(
        graph,
        graph_file
    )

    print("\nGraph saved to:")
    print(graph_file)

    return graph_file


# ---------------------------------------------------------
# Save graph features
# ---------------------------------------------------------

def save_graph_features(
    feature_df,
    centrality_df
):

    base_dir = Path(__file__).resolve().parent.parent

    output_dir = (
        base_dir
        / "data"
        / "processed"
    )

    feature_file = (
        output_dir
        / "graph_entity_features.csv"
    )

    centrality_file = (
        output_dir
        / "graph_centrality.csv"
    )

    feature_df.to_csv(
        feature_file,
        index=False
    )

    centrality_df.to_csv(
        centrality_file,
        index=False
    )

    print("\nGraph feature files:")
    print(feature_file)
    print(centrality_file)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("BITCOIN ENTITY GRAPH CONSTRUCTION")
    print("=" * 60)

    # Load data
    df = load_correlation_data()

    print(
        f"\nCorrelation records: {len(df)}"
    )

    # Prepare
    df = prepare_data(df)

    # Build graph
    graph = build_graph(df)

    print("\nGraph statistics:")
    print(
        f"Nodes: {graph.number_of_nodes()}"
    )

    print(
        f"Edges: {graph.number_of_edges()}"
    )

    # Graph features
    graph_features = calculate_graph_features(
        graph
    )

    # Centrality
    centrality = calculate_centrality(
        graph
    )

    # Save
    save_graph(graph)

    save_graph_features(
        graph_features,
        centrality
    )

    print("\n" + "=" * 60)
    print("GRAPH CONSTRUCTION COMPLETED")
    print("=" * 60)

    print("\nSample graph entities:")

    print(
        graph_features.head(15)
    )
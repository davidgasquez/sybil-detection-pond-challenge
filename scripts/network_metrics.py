#!/usr/bin/env python3
"""
Script to compute network metrics for blockchain addresses.
Focuses on fast metrics that can be computed efficiently.
"""

import time
import warnings
from pathlib import Path

import networkx as nx
import polars as pl

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure polars display settings
_ = pl.Config.set_tbl_rows(5)
_ = pl.Config.set_tbl_cols(20)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def main():
    """Load events data, create network graph, compute metrics, and save results."""
    print("Loading transaction data...")
    start_time = time.time()

    # Import data loading functions
    from sdpc.data import (
        joined_dex_swaps_df,
        joined_token_transfers_df,
        joined_train_df,
        joined_transactions_df,
        wallet_addresses_df,
    )

    # Load datasets
    transactions = joined_transactions_df()
    dex_swaps = joined_dex_swaps_df()
    token_transfers = joined_token_transfers_df()

    # Load address and training data
    train_df = joined_train_df().with_columns(pl.col("label").cast(pl.Int64))
    all_addresses = wallet_addresses_df()

    # Join with training labels
    all_addresses = all_addresses.join(
        train_df.select(["address", "label"]),
        on="address",
        how="left",
    )

    print(f"Data loaded in {time.time() - start_time:.2f} seconds")

    print("Creating events dataframe...")
    start_time = time.time()

    # Create combined events dataframe
    events: pl.DataFrame = (
        pl.concat([
            transactions.select(
                pl.col("FROM_ADDRESS"),
                pl.col("TO_ADDRESS"),
                pl.lit("tx").alias("TYPE"),
            ),
            dex_swaps.select(
                pl.col("ORIGIN_FROM_ADDRESS").alias("FROM_ADDRESS"),
                pl.col("TX_TO").alias("TO_ADDRESS"),
                pl.lit("dex-swap").alias("TYPE"),
            ),
            token_transfers.select(
                pl.col("FROM_ADDRESS").alias("FROM_ADDRESS"),
                pl.col("TO_ADDRESS").alias("TO_ADDRESS"),
                pl.lit("token-transfer").alias("TYPE"),
            ),
        ])
        .group_by(["FROM_ADDRESS", "TO_ADDRESS"])
        .agg(pl.count().alias("EVENTS"))
    )

    print(f"Events created in {time.time() - start_time:.2f} seconds")

    print("Building network graph from events...")
    start_time = time.time()

    # Filter out rows with None values in FROM_ADDRESS or TO_ADDRESS
    filtered_events = events.filter(
        (pl.col("FROM_ADDRESS").is_not_null()) & (pl.col("TO_ADDRESS").is_not_null())
    )

    # Create a network graph from the events dataframe
    G = nx.Graph()

    # Add edges with weights from the events dataframe
    for row in filtered_events.iter_rows(named=True):
        # Skip self-loops
        if row["FROM_ADDRESS"] == row["TO_ADDRESS"]:
            continue

        # Add edge with weight equal to the number of events
        G.add_edge(row["FROM_ADDRESS"], row["TO_ADDRESS"], weight=row["EVENTS"])

    # Apply filtering to reduce graph size (for efficiency)
    minimum_weight = 3  # Only keep edges with 3+ interactions
    edges_to_remove = [
        (u, v) for u, v, d in G.edges(data=True) if d["weight"] < minimum_weight
    ]
    G.remove_edges_from(edges_to_remove)

    print(
        f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges in {time.time() - start_time:.2f} seconds"
    )

    # Initialize metrics dictionary
    address_list = list(G.nodes())
    metrics_data = {"address": address_list}

    # ==== Fast Metrics ====

    # Degree - count of connections (very fast)
    print("Computing degree...")
    start_time = time.time()

    degrees = dict(G.degree())  # type: ignore
    metrics_data["degree"] = [degrees.get(node, 0) for node in address_list]

    print(f"Degree computed in {time.time() - start_time:.2f} seconds")

    # Degree centrality - normalized degree (very fast)
    print("Computing degree centrality...")
    start_time = time.time()

    degree_centrality = nx.degree_centrality(G)
    metrics_data["degree_centrality"] = [
        degree_centrality.get(node, 0) for node in address_list
    ]

    print(f"Degree centrality computed in {time.time() - start_time:.2f} seconds")

    # PageRank - measure of node importance (relatively fast)
    print("Computing PageRank...")
    start_time = time.time()

    pagerank = nx.pagerank(G, alpha=0.85, max_iter=100)
    metrics_data["pagerank"] = [pagerank.get(node, 0) for node in address_list]

    print(f"PageRank computed in {time.time() - start_time:.2f} seconds")

    # Eigenvector centrality - nodes connected to important nodes (moderately fast)
    print("Computing eigenvector centrality...")
    start_time = time.time()

    try:
        # Set max_iter to limit computation time, adjust if needed
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=100)
        metrics_data["eigenvector_centrality"] = [
            eigenvector_centrality.get(node, 0) for node in address_list
        ]
        print(
            f"Eigenvector centrality computed in {time.time() - start_time:.2f} seconds"
        )
    except nx.PowerIterationFailedConvergence:
        print("Eigenvector centrality calculation failed to converge. Skipping.")
        metrics_data["eigenvector_centrality"] = [0.0] * len(address_list)

    # Local clustering coefficient (moderately fast)
    print("Computing clustering coefficient...")
    start_time = time.time()

    clustering = nx.clustering(G)
    metrics_data["clustering_coefficient"] = [
        clustering.get(node, 0)  # type: ignore
        for node in address_list
    ]

    print(f"Clustering coefficient computed in {time.time() - start_time:.2f} seconds")

    # Core number - shell index of k-core decomposition (fast)
    print("Computing core number...")
    start_time = time.time()

    core_number = nx.core_number(G)
    metrics_data["core_number"] = [core_number.get(node, 0) for node in address_list]

    print(f"Core number computed in {time.time() - start_time:.2f} seconds")

    # Convert to polars dataframe
    metrics_df = pl.DataFrame(metrics_data, strict=False)

    # Add label information for analysis
    metrics_df = metrics_df.join(
        all_addresses.select(["address", "label", "split"]), on="address", how="left"
    )

    # Save metrics to CSV
    output_dir = PROJECT_ROOT / "data/processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "network_metrics.csv"
    metrics_df.write_csv(metrics_path)
    print(f"Network metrics saved to {metrics_path}")

    # Print summary statistics
    print("\nMetrics summary:")
    for col in metrics_df.columns:
        if col not in ["address", "label", "split"]:
            try:
                stats = metrics_df.select(
                    pl.col(col).min().alias("min"),
                    pl.col(col).mean().alias("mean"),
                    pl.col(col).median().alias("median"),
                    pl.col(col).max().alias("max"),
                )
                print(f"{col}: {stats}")
            except Exception as e:
                print(f"Could not compute statistics for {col}: {e}")


if __name__ == "__main__":
    main()

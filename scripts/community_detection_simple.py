#!/usr/bin/env python3
"""
Simplified script to create an events table and perform community detection.
"""

import warnings
from pathlib import Path

import networkx as nx
import polars as pl
from community import best_partition

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure polars display settings
_ = pl.Config.set_tbl_rows(5)
_ = pl.Config.set_tbl_cols(20)

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def main():
    """Main function to load data, create network, detect communities and save results."""
    print("Loading transaction data...")

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

    print("Creating labeled transaction datasets...")

    # Add labels to transactions
    transactions_with_labels = transactions.join(
        all_addresses.select(["address", "label"]).rename({
            "address": "FROM_ADDRESS",
            "label": "label_from",
        }),
        on="FROM_ADDRESS",
        how="left",
    ).join(
        all_addresses.select(["address", "label"]).rename({
            "address": "TO_ADDRESS",
            "label": "label_to",
        }),
        on="TO_ADDRESS",
        how="left",
    )

    # Add labels to dex swaps
    dex_swaps_with_labels = dex_swaps.join(
        all_addresses.select(["address", "label"]).rename({
            "address": "ORIGIN_FROM_ADDRESS",
            "label": "label_from",
        }),
        on="ORIGIN_FROM_ADDRESS",
        how="left",
    ).join(
        all_addresses.select(["address", "label"]).rename({
            "address": "ORIGIN_TO_ADDRESS",
            "label": "label_to",
        }),
        on="ORIGIN_TO_ADDRESS",
        how="left",
    )

    # Add labels to token transfers
    token_transfers_with_labels = token_transfers.join(
        all_addresses.select(["address", "label"]).rename({
            "address": "FROM_ADDRESS",
            "label": "label_from",
        }),
        on="FROM_ADDRESS",
        how="left",
    ).join(
        all_addresses.select(["address", "label"]).rename({
            "address": "TO_ADDRESS",
            "label": "label_to",
        }),
        on="TO_ADDRESS",
        how="left",
    )

    print("Creating events dataframe...")

    # Create combined events dataframe
    events: pl.DataFrame = (
        pl.concat([
            transactions_with_labels.select(
                pl.col("FROM_ADDRESS"),
                pl.col("TO_ADDRESS"),
                pl.lit("tx").alias("TYPE"),
                pl.col("label_from").alias("FROM_LABEL"),
                pl.col("label_to").alias("TO_LABEL"),
            ),
            dex_swaps_with_labels.select(
                pl.col("ORIGIN_FROM_ADDRESS").alias("FROM_ADDRESS"),
                pl.col("TX_TO").alias("TO_ADDRESS"),
                pl.lit("dex-swap").alias("TYPE"),
                pl.col("label_from").alias("FROM_LABEL"),
                pl.col("label_to").alias("TO_LABEL"),
            ),
            token_transfers_with_labels.select(
                pl.col("FROM_ADDRESS").alias("FROM_ADDRESS"),
                pl.col("TO_ADDRESS").alias("TO_ADDRESS"),
                pl.lit("token-transfer").alias("TYPE"),
                pl.col("label_from").alias("FROM_LABEL"),
                pl.col("label_to").alias("TO_LABEL"),
            ),
        ])
        .group_by(["FROM_ADDRESS", "TO_ADDRESS"])
        .agg(pl.count().alias("EVENTS"))
    )

    # No longer saving events.parquet

    print("Building network graph from events...")

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
    minimum_weight = 3  # Increased from 2 to 3
    edges_to_remove = [
        (u, v) for u, v, d in G.edges(data=True) if d["weight"] < minimum_weight
    ]
    G.remove_edges_from(edges_to_remove)

    print(
        f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges"
    )

    print("Detecting communities using Louvain algorithm...")

    # Apply Louvain community detection algorithm
    communities = best_partition(G)

    print(f"Detected {len(set(communities.values()))} communities")

    # Create a simple dataframe with just address and community
    community_data = {
        "address": list(communities.keys()),
        "community": list(communities.values()),
    }

    # Convert to polars dataframe
    community_df = pl.DataFrame(community_data)

    # No longer joining with labels and split

    # Save community mapping to CSV
    output_dir = PROJECT_ROOT / "data/processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    community_path = output_dir / "addresses_community_simple.csv"
    community_df.write_csv(community_path)
    print(f"Address to community mapping saved to {community_path}")

    # Report summary statistics
    print("\nCommunity size distribution:")
    community_sizes = community_df.group_by("community").agg(pl.count().alias("size"))
    print(community_sizes.sort("size", descending=True).head(10))


if __name__ == "__main__":
    main()

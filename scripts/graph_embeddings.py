#!/usr/bin/env python3
"""
Script to compute Node2Vec graph embeddings for blockchain addresses.
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


def create_graph():
    """Load events data and create network graph."""
    print("Loading transaction data...")
    start_time = time.time()

    # Import data loading functions
    # Ensure this module exists and functions are correctly defined
    try:
        from sdpc.data import (
            joined_dex_swaps_df,
            joined_token_transfers_df,
            joined_transactions_df,
        )
    except ImportError as e:
        print(f"Error importing data loading functions: {e}")
        print("Please ensure 'sdpc.data' module is set up correctly.")
        return None

    # Load datasets
    try:
        transactions = joined_transactions_df()
        dex_swaps = joined_dex_swaps_df()
        token_transfers = joined_token_transfers_df()
    except Exception as e:
        print(f"Error loading dataframes: {e}")
        return None

    print(f"Data loaded in {time.time() - start_time:.2f} seconds")

    print("Creating events dataframe...")
    start_time = time.time()

    # Create combined events dataframe
    events: pl.DataFrame = (
        pl.concat(
            [
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
            ],
            how="vertical_relaxed",
        )  # Use relaxed vertical concat
        .filter(  # Filter nulls early
            pl.col("FROM_ADDRESS").is_not_null() & pl.col("TO_ADDRESS").is_not_null()
        )
        .group_by(["FROM_ADDRESS", "TO_ADDRESS"])
        .agg(pl.count().alias("EVENTS"))
    )

    print(f"Events created in {time.time() - start_time:.2f} seconds")

    print("Building network graph from events...")
    start_time = time.time()

    # Create a network graph from the events dataframe
    G = nx.Graph()

    # Add edges with weights from the events dataframe
    # Use itertuples for potentially better performance with Polars >= 0.19.3
    for row in events.iter_rows(named=True):
        from_address, to_address, event_count = (
            row["FROM_ADDRESS"],
            row["TO_ADDRESS"],
            row["EVENTS"],
        )
        # Skip self-loops
        if from_address == to_address:
            continue
        # Add edge with weight equal to the number of events
        G.add_edge(from_address, to_address, weight=event_count)

    # Apply filtering to reduce graph size (for efficiency)
    # This is computationally intensive for large graphs initially,
    # Consider filtering edges *before* adding them if performance is critical
    minimum_weight = 3  # Only keep edges with 3+ interactions
    edges_to_remove = [
        (u, v) for u, v, d in G.edges(data=True) if d["weight"] < minimum_weight
    ]
    G.remove_edges_from(edges_to_remove)

    # Remove isolated nodes (nodes with no edges after filtering)
    isolated_nodes = list(nx.isolates(G))
    G.remove_nodes_from(isolated_nodes)

    print(
        f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges in {time.time() - start_time:.2f} seconds"
    )
    if G.number_of_nodes() == 0:
        print("Warning: Graph has no nodes after filtering. Cannot compute embeddings.")
        return None
    return G


def compute_node2vec_embeddings(G: nx.Graph, dimensions: int = 64, workers: int = 4):
    """Compute Node2Vec embeddings for the graph."""
    print(f"Computing Node2Vec embeddings (dimensions={dimensions})...")
    start_time = time.time()

    from node2vec import Node2Vec

    # Ensure nodes are strings for Node2Vec/Word2Vec compatibility if they aren't already
    # NetworkX nodes can be any hashable type. Word2Vec expects strings.
    # Check node types - if not string, create a mapping and relabel graph
    node_type = type(next(iter(G.nodes())))
    mapping = None
    if node_type is not str:
        print(f"Nodes are of type {node_type}. Relabeling to strings for Node2Vec.")
        mapping = {node: str(node) for node in G.nodes()}
        G = nx.relabel_nodes(G, mapping)

    # Precompute probabilities and generate walks
    node2vec = Node2Vec(
        G,
        dimensions=dimensions,
        walk_length=30,  # Length of walks
        num_walks=10,  # Number of walks per node (reduce from 200 for faster testing/initial run)
        workers=workers,  # Number of CPU cores
        weight_key="weight",  # Use edge weights
        p=1,  # Return parameter
        q=1,  # In-out parameter
        quiet=False,  # Show progress
    )

    # Train Node2Vec model (using gensim Word2Vec)
    # window: Context size
    # min_count: Ignore words with frequency lower than min_count
    # sg: 1 for skip-gram (usually better for embeddings), 0 for CBOW
    # hs: 1 for hierarchical softmax (good for infrequent words), 0 for negative sampling
    # negative: Number of negative samples (if hs=0)
    model = node2vec.fit(
        window=10, min_count=1, sg=1, hs=0, negative=5, epochs=3, batch_words=10000
    )  # Use fewer epochs for speed initially

    print(f"Node2Vec model trained in {time.time() - start_time:.2f} seconds")

    # Get embeddings for all nodes in the graph
    nodes = list(G.nodes())  # These are now guaranteed to be strings if relabeled
    # Ensure keys are strings (should be redundant now, but safe)
    embeddings_dict = {str(node): model.wv[str(node)] for node in nodes}

    # Convert embeddings to Polars DataFrame
    embedding_dim_names = [f"n2v_{i}" for i in range(dimensions)]

    # If we relabeled, map back to original node identifiers
    if mapping:
        original_nodes = list(mapping.keys())
        embeddings_list = [
            {
                "address": original_node,
                **{
                    name: val
                    for name, val in zip(
                        embedding_dim_names, embeddings_dict[str(original_node)]
                    )
                },
            }
            for original_node in original_nodes
            if str(original_node) in embeddings_dict  # Check if node exists in dict
        ]
    else:
        embeddings_list = [
            {
                "address": node,
                **{
                    name: val
                    for name, val in zip(embedding_dim_names, embeddings_dict[node])
                },
            }
            for node in nodes
            if node in embeddings_dict  # Check if node exists in dict
        ]

    if not embeddings_list:
        print("Error: No embeddings were generated.")
        return None

    embeddings_df = pl.DataFrame(
        embeddings_list, strict=False
    )  # Use strict=False initially

    # Cast address column back to original type if needed, or keep as string
    # Example: Cast back if original type was int
    # if mapping and node_type is int:
    #    embeddings_df = embeddings_df.with_columns(pl.col("address").cast(pl.Int64)) # Or appropriate type
    # Assuming addresses are strings (common in blockchain):
    embeddings_df = embeddings_df.with_columns(pl.col("address").cast(pl.Utf8))

    print(
        f"Embeddings extracted and converted to DataFrame in {time.time() - start_time:.2f} seconds"
    )
    return embeddings_df


def main():
    """Create graph, compute Node2Vec embeddings, and save results."""
    G = create_graph()

    if G is None:
        print("Graph creation failed or graph is empty. Exiting.")
        return

    # Define embedding dimensions and workers
    embedding_dimensions = 64  # Common choice, can be tuned
    num_workers = 4  # Adjust based on available CPU cores

    # Compute embeddings
    embeddings_df = compute_node2vec_embeddings(
        G, dimensions=embedding_dimensions, workers=num_workers
    )

    if embeddings_df is None:
        print("Embedding computation failed. Exiting.")
        return

    # Load address and training data to join labels/splits if needed
    print("Loading address data for joining...")
    start_time = time.time()
    try:
        from sdpc.data import (
            joined_train_df,
            wallet_addresses_df,
        )

        train_df = joined_train_df().with_columns(pl.col("label").cast(pl.Int64))
        all_addresses = wallet_addresses_df()
        all_addresses = all_addresses.join(
            train_df.select(["address", "label"]),
            on="address",
            how="left",
        )
        print(f"Address data loaded in {time.time() - start_time:.2f} seconds")

        # Add label information for analysis (optional, but good practice)
        embeddings_df = embeddings_df.join(
            all_addresses.select(["address", "label", "split"]),
            on="address",
            how="left",
        )
    except ImportError:
        print("Could not import address/train data, skipping join with labels/split.")
    except Exception as e:
        print(f"Error joining with address/train data: {e}")

    # Save embeddings
    output_dir = PROJECT_ROOT / "data/processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    # Using parquet for better type handling and compression with numeric data
    embeddings_path = output_dir / "node2vec_embeddings.parquet"
    embeddings_df.write_parquet(embeddings_path)
    print(f"Node2Vec embeddings saved to {embeddings_path}")

    # Print summary statistics
    print("Embeddings DataFrame head:")
    print(embeddings_df.head())


if __name__ == "__main__":
    main()

from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).parent.parent.parent


def joined_train_df() -> pl.DataFrame:
    eth_train = pl.read_parquet(
        PROJECT_ROOT / "data/raw/ethereum/train_addresses.parquet"
    ).select(pl.col("ADDRESS").alias("address"), pl.col("LABEL").alias("label"))

    base_train = pl.read_parquet(
        PROJECT_ROOT / "data/raw/base/train_addresses.parquet"
    ).select(pl.col("ADDRESS").alias("address"), pl.col("LABEL").alias("label"))

    all_addresses_df = pl.concat([
        eth_train.select("address"),
        base_train.select("address"),
    ]).unique()

    train_df = all_addresses_df.join(eth_train, on="address", how="left").join(
        base_train, on="address", how="left"
    )

    train_df = train_df.select(
        pl.col("address"),
        pl.max_horizontal(["label", "label_right"]).alias("label"),
    )

    return train_df


def joined_transactions_df() -> pl.DataFrame:
    eth_transactions = pl.read_parquet(
        PROJECT_ROOT / "data/raw/ethereum/transactions.parquet"
    ).with_columns(pl.lit("ethereum").alias("NETWORK"))

    base_transactions = pl.read_parquet(
        PROJECT_ROOT / "data/raw/base/transactions.parquet"
    ).with_columns(pl.lit("base").alias("NETWORK"))

    common_columns = [
        col for col in base_transactions.columns if col in eth_transactions.columns
    ]

    base_transactions = base_transactions.select(
        common_columns,
    )
    eth_transactions = eth_transactions.select(
        common_columns,
    )

    all_transactions = pl.concat(
        [eth_transactions, base_transactions], how="diagonal_relaxed"
    )

    return all_transactions


def joined_dex_swaps_df() -> pl.DataFrame:
    eth_dex_swaps = pl.read_parquet(
        PROJECT_ROOT / "data/raw/ethereum/dex_swaps.parquet"
    )
    base_dex_swaps = pl.read_parquet(PROJECT_ROOT / "data/raw/base/dex_swaps.parquet")

    eth_dex_swaps = eth_dex_swaps.with_columns(pl.lit("ethereum").alias("NETWORK"))
    base_dex_swaps = base_dex_swaps.with_columns(pl.lit("base").alias("NETWORK"))

    all_dex_swaps = pl.concat([eth_dex_swaps, base_dex_swaps])

    return all_dex_swaps


def joined_token_transfers_df() -> pl.DataFrame:
    eth_token_transfers = pl.read_parquet(
        PROJECT_ROOT / "data/raw/ethereum/token_transfers.parquet"
    )
    base_token_transfers = pl.read_parquet(
        PROJECT_ROOT / "data/raw/base/token_transfers.parquet"
    )

    eth_token_transfers = eth_token_transfers.with_columns(
        pl.lit("ethereum").alias("NETWORK")
    )
    base_token_transfers = base_token_transfers.with_columns(
        pl.lit("base").alias("NETWORK")
    )

    all_token_transfers = pl.concat([eth_token_transfers, base_token_transfers])

    return all_token_transfers


def test_data_df() -> pl.DataFrame:
    test_df = pl.read_parquet(
        PROJECT_ROOT / "data/raw/ethereum/test_addresses.parquet"
    ).rename({
        "ADDRESS": "address",
    })
    return test_df


def wallet_addresses_df() -> pl.DataFrame:
    train_df = joined_train_df()
    test_df = test_data_df()

    wallet_addresses = pl.concat([
        train_df.select("address").with_columns(pl.lit("train").alias("split")),
        test_df.select("address").with_columns(pl.lit("test").alias("split")),
    ])

    wallet_addresses = wallet_addresses.unique(subset=["address"], keep="first")

    return wallet_addresses


def all_addresses_df() -> pl.DataFrame:
    train_df = joined_train_df()
    test_df = test_data_df()
    transactions_df = joined_transactions_df()
    dex_swaps_df = joined_dex_swaps_df()
    token_transfers_df = joined_token_transfers_df()

    all_addresses = pl.concat([
        train_df.select("address"),
        test_df.select("address"),
        transactions_df.select("FROM_ADDRESS").rename({"FROM_ADDRESS": "address"}),
        transactions_df.select("TO_ADDRESS").rename({"TO_ADDRESS": "address"}),
        dex_swaps_df.select("ORIGIN_FROM_ADDRESS").rename({
            "ORIGIN_FROM_ADDRESS": "address"
        }),
        dex_swaps_df.select("ORIGIN_TO_ADDRESS").rename({
            "ORIGIN_TO_ADDRESS": "address"
        }),
        dex_swaps_df.select("SENDER").rename({"SENDER": "address"}),
        dex_swaps_df.select("TX_TO").rename({"TX_TO": "address"}),
        token_transfers_df.select("FROM_ADDRESS").rename({"FROM_ADDRESS": "address"}),
        token_transfers_df.select("TO_ADDRESS").rename({"TO_ADDRESS": "address"}),
        token_transfers_df.select("ORIGIN_TO_ADDRESS").rename({
            "ORIGIN_TO_ADDRESS": "address"
        }),
        token_transfers_df.select("ORIGIN_FROM_ADDRESS").rename({
            "ORIGIN_FROM_ADDRESS": "address"
        }),
    ]).unique()

    return all_addresses

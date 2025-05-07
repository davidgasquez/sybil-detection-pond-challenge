# Pond Sybil Detection Challenge 🕵️‍♂️

Sybil attacks have long been a challenge in Web3, affecting everything from airdrops and governance to funding mechanisms. These attacks occur when individuals create multiple fake identities to manipulate systems, gain unfair advantages, or exploit incentives.

The objective is to build a machine learning model that predicts the **probability** of a given wallet address being a sybil, using historical blockchain data.

## Resources 📚

- [Pond Competition](https://cryptopond.xyz/modelfactory/detail/4712551)

## Data 📊

For a given address, the desired output of the model is a score between 0 and 1 (0=non-Sybil, 1=Sybil) indicating how likely the given address is a Sybil wallet.

You are provided with a labeled dataset of **known Sybil addresses** sourced from **Gitcoin Passport and external Sybil lists **(LayerZero, zkSync, OP, Octant, and Gitcoin's internal ban lists). You will analyze wallet activities, including **transactions, token transfers, and DEX swaps**. Please feel free to use any other dataset that you find useful.

#### Known Sybil Addresses

A labeled dataset of approximately **2,500 known Sybil addresses** is provided. These addresses were flagged based on past **Sybil attack patterns, airdrop farming behaviors, and blockchain analytics**.

#### Test Addresses

A set of **unlabeled addresses** is provided for model evaluation. This dataset includes a **mix of human (non-Sybil) and Sybil wallets**, but their labels are withheld.

#### Ethereum & Base Transactions

Historical transactions for addresses involved in this competition are provided in the **transactions** table. Each transaction has a unique identifier (`TX_HASH`), the address initiating the transaction (`FROM_ADDRESS`), the address being interacted with (`TO_ADDRESS`), the amount of Ether transacted (`VALUE`), and other related information.

#### Transfers of the tokens

ERC-20 token transfers for wallet addresses on Ethereum and Base are provided in the **token_transfers** table. Each transfer inherits data such as `block_timestamp` and `tx_hash` from the associated transaction, but also contains parsed data including

- Sending address of the transfer (`From_Address`) which is not necessarily the same as the `From_Address` of the transaction
- Receiving address of the transfer (`To_Address`)
- Decimal-adjusted amount of the asset (`Amount_Precise`) and its USD value (`Amount_USD`). The USD value is not always available.
- Address of the token being transferred (`Contract_Address`)

#### DEX swaps

Not all wallets have traded on decentralized exchanges (DEX). For wallets that have, token swaps are recorded in the **dex_swaps** table. Each swap record contains `BLOCK_TIMESTAMP` and `TX_HASH` from the associated transaction, along with the following parsed data:

- The address of the token sent for swap (`TOKEN_IN`)
- The address of the token received in the swap (`TOKEN_OUT`)
- Amount of input token (`AMOUNT_IN`) and its USD value (`AMOUNT_IN_USD`), when available
- Amount of token received (`AMOUNT_OUT`) and its USD value (`AMOUNT_OUT_USD`), when available
- The address that initiated the swap (`ORIGIN_FROM_ADDRESS`)
- The address that receives the swapped token (`TX_TO`)

## Evaluation 📈

For each address in the test set, the model should output a **probability score** (ranging from 0 to 1) representing the likelihood of the address being Sybil. The prediction files will be evaluated once per week, and accordingly the leaderboard will be updated weekly.

The submissions will be evaluated using **AUC** (Area Under the ROC Curve).

## Submission File 📄

Once your model is ready, submit your predictions for the test addresses in a simple CSV file with two columns (The column names have to match below exactly or the evaluation will error out):

- `ADDRESS`: Wallet addresses from the test set.
- `PRED`: Your predicted Sybil likelihood (between 0 and 1).

## License 📜

This repository is licensed under the [MIT License](https://opensource.org/licenses/MIT).

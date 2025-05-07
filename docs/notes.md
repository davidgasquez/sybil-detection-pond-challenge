# Notes

## Open Questions

- Are all the wallets in the from / to clauses? What is the smallest set of pairs we need to build a proper grahp?
  - Differences between from_address and origin_from_address is Token transfers?
  - When plotting the network, should we use all 3 datasets or make 3 different networks?
- Are all TX in the TX dataset? Are DEX trades in the TX dataset? Are Token transfers in the TX dataset?
- Why are there wallets without transactions on Base or Ethereum?
  - E.g: 0xbeec6c7dd90ef9de123ea6e920cd20b7814e86a0

## TODO

- Add provisional sybil list to the preprocessing and postprocessing
- Transaction/Events Entropy
- Explore Undersampling
  - Send the same model + features, **with** and **without** undersampling
- Feature: Null count on the row
- Assign a higher misclassification penalty to the minority class (Sybil). Many classifiers (like XGBoost, LightGBM, Logistic Regression, SVMs) support class_weight='balanced'
- Check feature importances and think about features to add, update or remove
- Ensemble models!
- Whitelists here?
  - https://github.com/hop-protocol/hop-airdrop/tree/master/src/data
- Source of Funds Analysis
  - https://x.com/RobinsonBurkey/status/1806006206353346987
- Add features from Scott
  - https://mirror.xyz/scottonchain.eth/5aw8H6QD0PgUnj6luheFr4pqzBUGu5au9TVhKOY13s4
  - https://mirror.xyz/scottonchain.eth/8VZk2TyDV6ncRL1KgBINAiOF_60llJRhGKoMtbFKcZk
- More advanced algorithms
  - https://github.com/BrightID/BrightID-AntiSybil?tab=readme-ov-file#algorithms
- Add data from external APIs
  - Data from [Etherscan API](https://etherscan.io/address/0x128e14fcac5e8fa11202ed4582d332bb37e05e67)
  - https://intel.arkm.com/explorer/address/0xb9ecee9a0e273d8A1857F3B8EeA30e5dD3cb6335
  - [BitQuery API](https://explorer.bitquery.io/ethereum/address/0xfbcf4ab9f374e146009c2f7db2f659f2068b085f) ([GraphQL](https://bitquery.io/labs/graphql))
  - [Ethrank](https://www.ethrank.io/address/0xfbcf4ab9f374e146009c2f7db2f659f2068b085f)

## Feature Ideas

- Wallet Feature: con respecto a la fecha de la transacción fundacional, contar cuantas transacciones ha hecho el nodo origen en una ventana de 24h
- Transaction Count (Total): Total number of incoming and outgoing transactions.
- Transaction Frequency: Average number of transactions per unit of time (e.g., per day, per week) since account creation.
- ETH Balance: Current Ether balance of the wallet. (Sybils might maintain minimal balances).
- Total ETH Received: Sum of Ether received across all transactions.
- Total ETH Sent: Sum of Ether sent across all transactions.
- Net ETH Flow: Total ETH Received
- Total ETH Sent.
- Number of Unique Contracts Interacted With: Count of distinct smart contract addresses the wallet has sent transactions to.
- Time Since Last Transaction: Time elapsed since the most recent transaction.
- Average Time Between Transactions: Mean time difference between consecutive transactions (incoming or outgoing).
- Standard Deviation of Time Between Transactions: Variability in transaction timing.
- Activity Burstiness: Measures indicating if activity occurs in short, intense bursts (e.g., coefficient of variation of inter-transaction times).
- Timestamp Correlation: Analyze if transaction timestamps closely align with known Sybil clusters or specific events (like airdrop claim periods).
- First Active Date / Last Active Date: Timestamps of the very first and very last transactions.
- Average Gas Price Used: Mean gas price (Gwei) paid across transactions. (Sybils might use consistently low or identical gas prices).
- Total Gas Spent: Sum of gas fees paid across all transactions.
- Average Gas Limit Used: Mean gas limit set for transactions.
- Unique Incoming Addresses: Count of distinct addresses that sent ETH or tokens to the wallet.
- Unique Outgoing Addresses: Count of distinct addresses the wallet sent ETH or tokens to.
- Ratio of Unique Incoming/Outgoing: Unique Incoming / Unique Outgoing.
- Interaction with Centralized Exchanges (CEX): Boolean flag or count of interactions with known CEX deposit/withdrawal addresses.
- Interaction with DeFi Protocols: Boolean flag or count of interactions with known DEXs, lending protocols, etc.
- Interaction with Bridges: Boolean flag or count of interactions with known cross-chain bridges.
- Time between wallet creation (first transaction) and significant activity.
- Transaction Graph Metrics (Requires graph construction):
- In-Degree/Out-Degree: Number of unique senders/receivers (similar to unique counts above but in a graph context).
- Clustering Coefficient: Measure of how clustered the wallet's neighbors are.
- PageRank/Centrality Scores: Measures of importance/influence within the transaction graph.
- Calculate features separately for each chain (e.g., eth_tx_count, base_tx_count, eth_total_swap_volume, base_total_swap_volume).
- Calculate combined features (e.g., total_tx_count = eth_tx_count + base_tx_count).
- Calculate ratio features (e.g., eth_tx_count / total_tx_count).
- Features indicating potential bridging activity (e.g., interaction with known bridge contracts).
- Detection of Specific Motifs: Identifying patterns like fan-out (one address funding many) or fan-in (many addresses sending to one).
- Number of Token Types Held: Count of distinct ERC-20/ERC-721 tokens currently held (requires tracking transfers).
- Number of Token Types Transferred: Count of distinct token types ever transferred (in or out).
- Total Token Transfers (Incoming/Outgoing): Count of all ERC-20/ERC-721 transfer events.
- Value of Tokens Held/Transferred: Estimated USD or ETH value (requires price oracles/historical data, can be complex).
- Airdrop Token Interaction: Boolean flag or count of interactions with specific, known airdropped tokens. (Sybils often farm airdrops).
- Token Portfolio Similarity: Measure of how similar the wallet's token holdings are to other wallets (especially suspected Sybils).
- Frequency of Token Swaps: Number of interactions with DEX swap functions.
- Initial Funding Source: Address that first sent ETH to the wallet. Check if it's a known CEX, a known Sybil funder, or a fresh wallet.
- Initial Funding Amount: Amount of ETH received in the first transaction. (Sybils often receive small, identical amounts).
- Funding Pattern: Whether the wallet was funded once or received multiple small funding transactions, potentially from the same source(s).
- Contract Creator: Boolean flag indicating if the wallet has deployed any smart contracts. (Sybils rarely deploy contracts).
- Specific Function Calls: Frequency of calls to specific functions known to be related to Sybil activities (e.g., claim(), transfer(), multisend()).
- https://x.com/omeragoldberg/status/1791620500193427647
  - Identify user funding origin, focusing on CEX/DEX and bridges (over 50% of funders).
  - Mark the first native token transfer to each account as the funding transaction.
  - Trace LZ user funding txes, over 24hr timeframe and cluster known entities
  - Large-Scale Funding:  Over X wallets funded within the same 24-hour timeframe.
  - Identical Funding Sources: Txes originating from the same source
  - Behavioral Similarities: Users w/ similar patterns in their transactions.
  - Funding Amount: First funding amount for each wallet (in native token).
  - Number of Transactions to LayerZero: A comparable number of transactions directed towards the LayerZero protocol.

## AI

- https://g.co/gemini/share/30dd9d6d0740
- https://chatgpt.com/share/680762a9-4468-800e-a8b8-00974447f6d7

## Resources

- https://roundoperations.gitcoin.co/round-operations/post-round/cluster-matching-and-csv-upload
- https://github.com/cryptoamy/layerzero_sybil_scan_report
- https://github.com/0x9simon/slaysybil
- https://trusta-labs.gitbook.io/trustalabs/trustscan/q-and-a-for-sybil-score
- https://trustalabs.ai/trustscan
- https://github.com/TrustaLabs/Airdrop-Sybil-Identification
- https://common.xyz/layerzero/discussion/19475
- https://x.com/omeragoldberg/status/1791620500193427647
- https://mirror.xyz/scottonchain.eth/5aw8H6QD0PgUnj6luheFr4pqzBUGu5au9TVhKOY13s4
- https://github.com/hakymulla/HackFS-2023
- https://www.alchemy.com/dapps/top/identity-tools
- https://x.com/RobinsonBurkey/status/1806006206353346987
- https://mirror.xyz/0xC0e09A112Ae45d87597CD78c11b7D95a55aCC5F0/pWO_AAM9ZJzO0_HjyBztiUnGMZe9wJ7c0MWJr0x8adE
- https://docs.openrank.com/
- https://github.com/poupou-web3/GC-ODS-Sybil
- https://app.octan.network/reputation-board?address=0x4a3e6E66f8C32bC05A50879f872B1177A1573CDF
- https://mirror.xyz/scottonchain.eth/ijq3YmxPs1RSvXuFQvUbW3ZVIDWR4xObpslKCO0Zchg
- https://common.xyz/layerzero/search?q=sybil&communityScope=layerzero&sort=Best
  - https://common.xyz/layerzero/discussion/18713-submission
  - https://common.xyz/layerzero/discussion/22360-sybil-report-ruslan3
  - https://common.xyz/layerzero/discussion/21787-sybil-hunting-report-ruslan2
  - https://common.xyz/layerzero/discussion/18713-submission
  - https://common.xyz/layerzero/discussion/20043
  - https://common.xyz/layerzero/discussion/18712?comment=83274
  - https://common.xyz/layerzero/discussion/19280
  - https://common.xyz/layerzero/discussion/22086-cross-chain-sybil-addresses
- https://github.com/eltontay/Ethereum-Fraud-Detection
- https://research.nansen.ai/articles/linea-airdrop-sybil-detection
- https://medium.com/layerzero-official/addressing-sybil-activity-a2f92218ddd3
- https://www.kaggle.com/datasets/vagifa/ethereum-frauddetection-dataset
- https://www.kaggle.com/competitions/ieee-fraud-detection/code
- https://www.kaggle.com/datasets/gescobero/ethereum-fraud-dataset/data
- https://www.kaggle.com/datasets/chaitya0623/ethereum-transactions-for-fraud-detection
- https://github.com/frwd-1/sybil-defender
- https://nomis.cc scoring
- https://dorahacks.io/buidl/3140
- https://mirror.xyz/scottonchain.eth/jYzIs6rFmQC7Ox5W5o-81gFAXIwAAB332TeATwL9ymc
- https://mirror.xyz/scottonchain.eth/8VZk2TyDV6ncRL1KgBINAiOF_60llJRhGKoMtbFKcZk
- https://mirror.xyz/x-explore.eth/AFroG11e24I6S1oDvTitNdQSDh8lN5bz9VZAink8lZ4
- https://x.com/MayankG37475182/status/1889537784395997538
- https://github.com/ArbitrumFoundation/sybil-detection
- https://github.com/gitcoinco/gitbook-KB/blob/93ad0800f54693633edfa8b2f572d102ff8d9a43/SUMMARY.md?plain=1#L97
- https://github.com/OpenDataforWeb3/Resources/blob/62185932b18bdfeaee66ba0426cfddd33bfaf590/docs/Legos.md?plain=1#L6
- https://github.com/BrightID/BrightID-AntiSybil - https://gov.gitcoin.co/t/what-can-we-learn-from-brightids-aura-sybil-defense-software/11159
- https://www.onchainscore.xyz/ is Coinbase API
- https://docs.cdp.coinbase.com/reputation/docs/welcome
- https://warpcast.com/purplefire/0xC3f39a4CbCc61209a3d0e3E944D5b94ad3B77fDc
- https://dune.com/queries/3765873
- https://github.com/search?q=Sybil%20List&type=repositories
- https://github.com/Uniswap/sybil-list
- https://github.com/stanlagermin/sybil-wallet-list
- https://docs.holonym.id/for-developers/custom-sybil-resistance
- https://github.com/opensource-observer/oso/blob/ce53a963786373374339d39271b63e43a86d179f/apps/docs/docs/contribute-models/challenges/2024-07-30-openrank.md?plain=1#L6
- https://x.com/artemis_onchain/status/1800463892352782345?ref=research.portexai.com
- https://docs.google.com/spreadsheets/d/1dRUCGxqW_SDCKbdvkvbPJLGHVifWTMY10-fSQw_7hOs/edit?gid=0#gid=0
- https://docs.google.com/spreadsheets/d/1UT8cQbRDSaBduGTcBO6zZKH_4n_02r_cSCl2FflvM14/edit?gid=0#gid=0
- https://mirror.xyz/wusimpl.eth/tUT-P7xCk_jNwdNLbVRe7hNAHgOEb3PNtue_zX2UhD4

# Notes

## TODO

- Add provisional sybil list to the preprocessing and postprocessing.
- Transaction/Events Entropy
- Explore Undersampling (Tomek Links, NearMiss, SMOTE)
- Assign a higher misclassification penalty to the minority class (Sybil)
  - Many classifiers (like XGBoost, LightGBM, Logistic Regression, SVMs) support `class_weight='balanced'`
- Ensemble best submissions

## APIs

- [Etherscan API](https://etherscan.io/address/0x128e14fcac5e8fa11202ed4582d332bb37e05e67)
- [Intel.arkm.com](https://intel.arkm.com/explorer/address/0xb9ecee9a0e273d8A1857F3B8EeA30e5dD3cb6335)
- [BitQuery API](https://explorer.bitquery.io/ethereum/address/0xfbcf4ab9f374e146009c2f7db2f659f2068b085f) ([GraphQL](https://bitquery.io/labs/graphql))

## Features

- Add features from Scott
  - https://mirror.xyz/scottonchain.eth/5aw8H6QD0PgUnj6luheFr4pqzBUGu5au9TVhKOY13s4
  - https://mirror.xyz/scottonchain.eth/8VZk2TyDV6ncRL1KgBINAiOF_60llJRhGKoMtbFKcZk
- Null counts on the row
- How many transactions in the first 24 hours?
- ETH Balance
- Total ETH Received
- Total ETH Sent
- Time Since Last Transaction
- Initial Funding Amount
- Is Contract Creator?
- [Source of Funds](https://x.com/RobinsonBurkey/status/1806006206353346987). User funding origin, focusing on CEX/DEX and bridges (over 50% of funders).

## Resources

- https://github.com/BrightID/BrightID-AntiSybil?tab=readme-ov-file#algorithms
- https://roundoperations.gitcoin.co/round-operations/post-round/sybil-analysis
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
- https://nomis.cc
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
- https://mirror.xyz/wusimpl.eth/tUT-P7xCk_jNwdNLbVRe7hNAHgOEb3PNtue_zX2UhD4

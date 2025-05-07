Title: Sybil Detection by XGBoost

URL Source: https://mirror.xyz/scottonchain.eth/5aw8H6QD0PgUnj6luheFr4pqzBUGu5au9TVhKOY13s4

Markdown Content:
Public blockchains are transparent, accurate, and comprehensive records of their entire history. These freely available data sets are some of the largest and cleanest in the world, and they are highly amenable to the application of machine learning.

In 2024, the Ethereum blockchain has about 200 million addresses, which is the same as the count of active websites on the internet. It is a global, public, financial dataset of internet scale.

Ranking, classification, personalization, co-occurrence models, and collaborative filtering are all directly applicable to real-world problems on the blockchain. Deep learning, especially LSTMs and sequential models, are also highly valuable, for example, in predicting what a user or address is likely to do next.

In this article, we walk through training of an XGBoost model for sybil detection on the Ethereum blockchain. Sybil attacks are a type of malicious activity on peer-to-peer networks, where a single entity impersonates many. Mitigating sybil attackers is crucial for maintaining the integrity of decentralized systems. For example, when an onchain network or application distributes a token in an “airdrop” to its users, it is common for attackers to use many addresses, impersonating multiple users in an attempt to multiply their reward.

This article is intended for data scientists and applied scientists working in blockchain analytics, as well as scientists from traditional fields, who are interested in an application of machine learning to new domain. It is detailed enough that a reader with working knowledge of `scikit-learn` and machine learning methodology can reproduce, and potentially improve, the result.

A high-level understanding of the approach described in this paper is also useful to technical product managers seeking effective sybil mitigation.

LayerZero Airdrop Sybil Detection
---------------------------------

[LayerZero](https://layerzero.network/), a cross-chain protocol, announced an airdrop in December 2023. Between the announcement and the distribution of tokens in June 2024, LayerZero went through a rigorous sybil detection process. The process included [community detection algorithms such as those used to mitigate sybils in the first Arbitrum airdrop](https://github.com/ArbitrumFoundation/sybil-detection), a [self-reporting bounty for sybil attackers](https://medium.com/layerzero-official/addressing-sybil-activity-a2f92218ddd3), and a crowdsourced sybil detection challenge, open to the general public. LayerZero cross-checked the results across sources, for example, applying k-means methodologies to validate the crowdsourced results. For this reason, [the final sybil list reported by LayerZero](https://flipsidecrypto.github.io/external-models/#!/model/model.external_models.layerzero__fact_transactions_snapshot) is considered a good source of truth for actual sybil detection.

There are known problems with the final LayerZero list, such as inclusion of [the operating wallet of the cross-chain DEX Layerswap](https://etherscan.io/address/0x2fc617e933a52713247ce25730f6695920b3befe), and many [reported false positives](https://commonwealth.im/layerzero/discussions/Final%20RFP%20Review). In spite of the known noise, this file is an excellent source of truth, and it allows application of traditional machine learning methodology to the problem of sybil detection.

LayerZero allows dapps to bridge across networks, including Ethereum, Binance Smart Chain, Arbitrum, and many others. For this article, we consider addresses from Ethereum who have interacted with the LayerZero protocol.

Increasingly, blockchain data is available in environments and platforms that replicate the user experience of more traditional data intelligence platforms, making it easy to extract and transform in a familiar way.

Excellent cloud platforms for extracting and transforming blockchain data include [Hyperline](https://www.hyperline.xyz/) and [Flipside](https://flipsidecrypto.xyz/). Flipside offers a very powerful [free account](https://docs.flipsidecrypto.xyz/welcome-to-flipside/data/choose-your-flipside-plan/free), sufficient for extracting features for this XGBoost model.

The [fact\_transactions\_snapshot](https://flipsidecrypto.github.io/external-models/#!/model/model.external_models.layerzero__fact_transactions_snapshot) table contains all addresses which have interacted with the LayerZero endpoint, including all chains. The CTE in the query extracts the Ethereum addresses only.

_Note: The QUALIFY clause chunks the data due to the limitations of the Flipside free account, allowing csv download of 100k lines at a time. There are just over 400k addresses to download, involving 5 queries and 100k chunks._

For all Ethereum transactions prior to the LayerZero snapshot on May 1, 2024, [this query](https://github.com/scottonchain/layerzero_xgboost/blob/main/feature_extraction/extract_l0_features_flipside.sql) calculates key features.

**LayerZero-Related Features**

*   `n_eth_interactions`: The number of interactions from the address to the LayerZero protocol, from the Ethereum chain. In particular, if the same address is used with LayerZero across chains, only Ethereum interactions with LayerZero are counted.

*   `source_chains_with_interactions`: The count of source chains the address has bridged using the LayerZero protocol. Similarly for `dest_chain_interactions`.

*   `n_cross_chain_interactions`: The total count of interactions from the address, from any chain to any chain.

*   `max_stargate_swap, avg_stargate_swap`: Metrics related to Stargate swaps using the LayerZero protocol, measured in USD.


**Ethereum-Related Features**

*   `out_degree`: The number of unique wallet addresses the `from_address` has sent transactions to, representing the out-degree of the address in the transaction graph. Similarly, `in_degree` is the number of addresses sending transactions to the node.

*   `earliest_transaction_time_out, latest_transaction_time_out`: The number of days between the earliest outgoing transactions and the date LayerZero took a snapshot for sybil detection (`2024-05-01`).

*   `time_span_day_out` : The difference between the preceding values measured in fractional days. The derived features `out_addresses_per_day_out` and `amount_per_day_out` were discovered to be accretive to metrics through domain knowledge and feature engineering.

*   `max_tx_value, min_tx_value, max_tx_value_in, etc`: Metrics related to the value of outgoing and incoming transactions, measured in ETH.

*   `max_tx_fee, min_tx_fee, max_tx_fee_in, etc`: Metrics related to the gas fee for outgoing and incoming transactions, measured in ETH. Note that transaction fees are particularly interesting, because sybil attackers try to avoid high gas prices to maximize ROI.

*   `n_avg_project_per_source_chain`: The average number of distinct projects using the LayerZero prototocol from the source chain.


Loading the entire dataset into a python dataframe is feasible on a local machine.

Training, Test, and Validation
------------------------------

Using the [fact\_transactions\_snapshot](https://flipsidecrypto.github.io/external-models/#!/model/model.external_models.layerzero__fact_transactions_snapshot) table as a truth set, we assign a label column called `sybil`, which is `TRUE` if the `addr` column is found in `fact_transactions_snapshot` and `FALSE` if not.

\`\`\`
# Not shown: Load fact_transaction_snapshot into address_df.
# Normalize addresses and column names as needed to lowercase

df['sybil'] = df['addr'].isin(address_df['address'])

# Calculate included/excluded stats
num_included = df['sybil'].sum()
num_excluded = len(df) - num_included

# Save a copy of the DataFrame and drop unnecessary columns
master_df = df.copy()
master_df.drop(columns=['addr'], inplace=True)

print(f"Percent sybils: {num_included / num_excluded}")
\`\`\`

\`\`\`
Percent sybils: 0.043740812267604415
\`\`\`

About 4.4% of the Ethereum addresses who interacted with LayerZero are sybils. Since we are interested in binary classification, we balance this training set.

We divide the data into 70% training and 30% test, reserving 30% of the training set for validation prior to balancing.

\`\`\`
# Separate features and labels
X = master_df.drop(columns=['sybil'])
y = master_df['sybil']

X_train_initial, X_test, y_train_initial, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_train_initial, y_train_initial, test_size=0.3, random_state=42, stratify=y_train_initial)

train_df = pd.concat([X_train, y_train], axis=1)
majority_class = train_df[train_df['sybil'] == 0]
minority_class = train_df[train_df['sybil'] == 1]

minority_class_upsampled = resample(minority_class,
                                    replace=True,
                                    n_samples=len(majority_class),
                                    random_state=42)

balanced_train_df = pd.concat([majority_class, minority_class_upsampled])

# Separate balanced features and labels for training
X_train_balanced = balanced_train_df.drop(columns=['sybil'])
y_train_balanced = balanced_train_df['sybil']
\`\`\`

XGBoost Classification of Sybils
--------------------------------

Training an XGBoost model with default parameters gives a promising initial result on the validation set. We start with `2000` epochs, based on initial experimentation showing that larger numbers of trees generalize better to the validation set in terms of `F1`, and to capture a learning curve against the loss function, `logloss`.

\`\`\`
params = {
    'objective': 'binary:logistic',
    'random_state': 42,
    'eval_metric': 'logloss',
    'n_estimators': 2000
}

# Create and train the XGBoost classifier
model = XGBClassifier(**params)
model.fit(X_train_balanced, y_train_balanced, verbose=False)

# Make predictions on the validation set
y_probs_val = model.predict_proba(X_val)[:, 1]  # Get probabilities for the positive class
y_pred = (y_probs_val > 0.5).astype(int)

print("\nClassification Report (Validation Set):")
print(classification_report(y_val, y_pred))

Output:

Classification Report (Validation Set):
              precision    recall  f1-score   support

       False       0.99      0.99      0.99     87427
        True       0.74      0.71      0.73      3824

    accuracy                           0.98     91251
   macro avg       0.86      0.85      0.86     91251
weighted avg       0.98      0.98      0.98     91251
\`\`\`

Without tuning, precision is already `0.74` on the training set, with recall of `0.71`.

The epoch-based learning curve against logloss (the training objective) shows a clear overfitting pattern, with the validation logloss reaching a minimum at `0.081` at epoch `709` for this representative training run. Beyond epoch `709`, the validation logloss slightly increases. The `F1` plot does not show the same degree of overfitting, and, indeed setting `n_estimators` to `709` does not substantially impact the `F1` score on the validation set.

![Image 1](https://images.mirror-media.xyz/publication-images/ki8NzZWCEJZKPbFjCZBmm.png)

Selecting subsets of the training data and plotting against F1 again shows that the model is overfitting.

\`\`\`
train_sizes = np.linspace(0.1, 1.0, 10)
train_scores = []
val_scores = []

for train_size in train_sizes:
    n_train = int(train_size * len(X_train_balanced))

    indices = np.random.choice(len(X_train_balanced), n_train, replace=False)
    X_train_subset = X_train_balanced.iloc[indices]
    y_train_subset = y_train_balanced.iloc[indices]

    model.fit(X_train_subset, y_train_subset)

    train_pred = model.predict(X_train_subset)
    train_f1 = f1_score(y_train_subset, train_pred, pos_label=True)
    train_scores.append(train_f1)

    val_pred = model.predict(X_val)
    val_f1 = f1_score(y_val, val_pred, pos_label=True)
    val_scores.append(val_f1)


train_mean = np.mean(train_scores)
val_mean = np.mean(val_scores)
train_std = np.std(train_scores)
val_std = np.std(val_scores)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_scores, label='Training F1 Score', color='blue', marker='o')
plt.plot(train_sizes, val_scores, label='Validation F1 Score', color='green', marker='o')
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, color='blue', alpha=0.1)
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, color='green', alpha=0.1)
plt.title('Learning Curve for XGBoost Classifier')
plt.xlabel('Training Size')
plt.ylabel('F1 Score')
plt.legend(loc='best')
plt.grid()
plt.show()
\`\`\`

Note that we use the held-out validation set to evaluate, rather than cross-validation. The training set is upsampled with replacement. Because the sybil examples are replicated many times in the training set, cross-validation would be subject to leakage of training observations to the cross-validation set.

A plot of F1 vs training set size is below. The model is able to predict on the training set with close to 100% accuracy, even with very small training set sizes, while the validation learning curve reaches a maximum at 80% of the training data, then slightly declines.

This is, in part, due to the upsampling of the minority class in the training set. Nonsybils are replicated on average more than 20 times for training, allowing the model to very closely match the training data.

![Image 2](https://images.mirror-media.xyz/publication-images/stOjKcIuXlMgxOG6jtFoK.png)

Overfitting suggests that tuning of related hyperparameters may improve performance on the validation set. A directed grid search leads to this optimization.

\`\`\`
learning_rate: 0.01
max_depth: 500
min_child_weight: 1
n_estimators: 1750
subsample: 0.5
\`\`\`

The same grid search shows that regularization parameters α\\alpha, γ\\gamma, and λ\\lambda are close to optimal at their defaults: α\=0 \\alpha=0, γ\=0\\gamma=0, λ\=1\\lambda=1.

These optimizations yield 1-2 percentage points for precision, recall, and F1, and the metrics generalize well to the test set.

\`\`\`
Classification Report (Optimal Threshold, Validation Set):
              precision    recall  f1-score   support

       False       0.99      0.99      0.99     87427
        True       0.75      0.73      0.74      3824

    accuracy                           0.98     91251
   macro avg       0.87      0.86      0.87     91251
weighted avg       0.98      0.98      0.98     91251

Classification Report (Optimal Threshold, Test Set):
              precision    recall  f1-score   support

       False       0.99      0.99      0.99    124895
        True       0.75      0.69      0.72      5463

    accuracy                           0.98    130358
   macro avg       0.87      0.84      0.85    130358
weighted avg       0.98      0.98      0.98    130358
\`\`\`

Application and Next Steps
--------------------------

We saw that tuning hyperparameters can increase the F1-score of this model by 1-2 percentage points. Feature selection and recursive feature elimination can give slight improvements, not shown here, as well as early stopping. For more substantial gains in accuracy, additional features are needed from the original dataset. Some are easy to obtain by modification of the above query, for example, metrics about the transaction value and gas fees coming into an address. Some are more computationally expensive, for example, graph-based features like the [Pagerank-based Reputation Score from Octan Network](http://1id.network/), the node clustering coefficents, and in-out ratios.

While additional feature extraction can improve the model beyond the scores shown here, the current model already has direct applications to sybil mitigation. Consider the precision-recall curve.

![Image 3](https://images.mirror-media.xyz/publication-images/xnmI9UM7QTneGy9U8X29M.png)

This curve shows that, if we capture the top `13%` of sybils (`13%` recall) with this model, then `98%` of the addresses identified as sybils are actually sybils. This kind of analysis can be useful when determining criteria for airdrops or other sybil-sensitive business operations. For some business purposes, this is sufficiently accurate, but, as this and related models improve, the tradeoff becomes better and better.

Conclusion
----------

This article has shown how to apply the XGBoost model to sybil mitigation, one of the biggest challenges in the blockchain industry. As scientists and engineers start to more broadly apply machine learning to the blockchain, the performance of these models is becoming better and better. A blockchain is an ideal dataset for machine learning: big, clean, freely available, and of value to individuals and larger entities.

Acknowledgement
---------------

_With gratitude to my colleagues at [Octan Network](https://1id.network/), especially [Paven Do](https://www.linkedin.com/in/paven-do/) and [Long Thanh (Chandler) Ta](https://www.linkedin.com/in/longthanhta/), for extremely valuable collaboration._

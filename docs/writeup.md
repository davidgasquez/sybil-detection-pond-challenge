# Sybil Detection Challenge

> https://discuss.octant.app/t/write-up-for-models-predicting-sybil-scores-of-wallets/696

Hello folks! Here are some details about the approach I took on the Sybil Detection Challenge.
It was a great contest and made me explore new techniques I wasn't familiar with (e.g: node2vec).
I'll be sharing the path instead of only the "final" setup as I think it's interesting in this case.
Before jumping into that, here are some of the most interesting reads I've found while researching for this competition.

- https://github.com/ArbitrumFoundation/sybil-detection

## Improving the Baseline

My first step was to get a baseline model going.
It's really useful to have an end to end thing working as soon as possible to make iterations easier and faster.
I then submitted a couple of dummy predictions (all `pred`s to 0.5) just to make sure they worked.

Once the model was setup, I added some stats from the provided datasets.
Simple aggregations like number of transactions, total value in/out, ...
Adding these features and changing the model to a Random Forest started producing ROC AUC scores around 0.98 on a 5 fold local cross validation.
This is interesting as it means the models are able to learn really well the training dataset.
The results on the leaderboard data where different, though (ROC AUC around 0.8).
That meant the `test` set has a different distribution of sybil wallets (training is around 3% while test might be around 10%).

While exploring the `test` set to verify that hunch, I continued adding all the features I could think of from the provided datasets.

## Adding Features

I added more aggregations at different levels (transaction, network, ...), and also for the different wallets (`from` will produce aggregations for senders and `to` for receivers). Doing this over most of the column resulted in around 200 features. Some of the most interesting ones:

- When that wallet received its first and last transactions
- Number of unique tokens it used
- How many wallets have interacted with it and with how many wallet has it interacted
- Data about the address it funded the wallet (label, value of first tx, id, ...). The goal was to get information about the founding event.

Adding these features raised the ROC AUC score to 0.9904, which confirmed the initial suspition that the training data didn't contain much more predictive power.

Nonetheless, I continue adding more features. Many of them were hand crafted features based on intuition (ratios, activity metrics, ...) but also spent a large amount of time trying to derive useful features from the interaction graph that these wallet form.

[Add graphext chart]

Once I constructed the graph, I was able to extract many interesting new features:

- Classic graph metrics like Degree, PakeRank, Centrality, Cluster, ...
- Levain community clusters and it's population size
- An embedding (64 values) of each wallet in the graph

This turned out to be important. Specially since it gives use more values we can "Target Encode".
The important one is the "community" and the "degree". Basically, you're giving the model the average sybil-ness of it's communiy and of people that interacted with the same number of wallets.

This moved the score to 0.9984.

## Cleaning Data

Another thing I realized while testing out thigns is that the training data contained some addresses that were contracts.
And seems the same thing happens within the `test` dataset.

That means that, if we get a list of contracts, we can mark these as "non sybil". It'll make our training dataset cleaner and ensure some accurate predictions in tests.

I got the data from a couple of Dune/Flipside queries, joined it, and did some lightweight preprocessing.

## Improving the Models

Since the start, I knew my model had a few problems:

- Too many columns.
- I was discarding the Datetime Features.
- Categorical features where being label encoded instead of OOE.

I spent some time improving the model pipeline to fix that. Added a feature selection step to keep only 100 features based on importance. Processed properly the datetime and categorical features. And, finally, moved to LGBM instead of Random Forests.

With all of this the local ROC AUC was of 0.99912. I'm sure there are a few more things that can be done (like subsampling with NearMiss or similar) but didn't want to spend more time trying out things if the score was already that close to 1.

How could I check the generalizability of this approach? Well, there is another Pond competition that has the same exact training data.
I downloaded it, changed the `read_csv()` to these files, run the model with `predict` instead of `predict_proba` and sent the submission (I had sent a dummy one earlier to check the shape). The result was promising.

Since the evaluation windows were taking their time. I started working on a different approach and changed the shape of the problem to "Event Sequence Classification". That means I would build a model that took a bunch of events (sent tx, swapped, sent another tx) and categorize them as sybil or not. Unfortunately, I wasn't able to finish with this approach as I got stuck figuring out the metadata and how to make a model understand that. This is something companies do a lot, for example, when predicting a trial conversion or if an user will churn.

## Postprocessing

## Conclussion

Another side-learning is that these kind of competitions will train models that overfit the sybil types that have been seen in the training data. If a sybil wallet is on the training data but not marked as sybil, the model will learn to classify it as non-sybil and the model will be trained to ignore these. Here, more than in other type of competitions, is where we need a plurality of models, each trained with different approaches and datasets.

---

- External sybil lists
- Passports was a good postprocessing step.
- Old passport scores
- High probability out of fold predictions to update the test set
- Since the evaluations were very slow, I couldn't learn much about the submissions and what worked
- "You're training a model for the known Sybil's"
- Data leakage as in many other competitions (passport scores, sybil lists)
- Compile list resources (notes.md)
- Funding sources for each wallet

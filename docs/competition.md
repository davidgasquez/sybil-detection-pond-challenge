# Competition

This is a ML challenge where I have to predict if **an Ethereum wallet is a Sybil or not**.

There are several datasets available:

- A list of labeled wallets (sybil or not).
  - This is our training dataset.
  - This is the resolution at which we want to predict.
- Transactions. Data about transactions on Ethereum and Base for the training wallets. Source: Flipside Crypto.
- DEX Swaps. Data about dex swaps on Ethereum and Base for the training wallets. Source: Flipside Crypto.
- Token Transfers. Data about token transfers on Ethereum and Base for the training wallets. Source: Flipside Crypto.

We need to build a training dataset at the wallet level. Deriving features from the 3 datasets above.

## Insights

- The training dataset distribution of Sybil wallet is not the same as in the test set. Training is around 3% while test is around 10%.
- The training data contains some wallets that are contracts or well known wallets (CEX, etc).
- We have an Humanity Score for each test wallet. The score is between 0 and 100 (likely human). We can't trust 0's to be all sybil but we can trust 100's to be all human. There is a range of scores for human wallets we can add to the postprocessing step.

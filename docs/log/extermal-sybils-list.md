# External Sybils List

There are many sybils lists out there, some of them are public. I want to use them as training data for the model.
It'll learn if it correlates with the target variable.

## TODO

- Is this a whitelist?
  - https://github.com/hop-protocol/hop-airdrop/tree/master/src/data

## LayerZero Sybil Report

LayerZero [created a repository](https://github.com/LayerZero-Labs/sybil-report) (now deleted) for people to report or identify sybil addresses. The process, from what I can tell was to create issues with the addresses and some context or justification.

The [Internet Archive](https://web.archive.org/web/20240524040829/https://github.com/LayerZero-Labs/sybil-report/blob/main/initialList.txt) shows some data.

GitHub Archive has the historical data for the repository too. We can get all the addresses from the issues and comments doing some fun SQL and regex magic.

```sql
with base as (
  SELECT DISTINCT
  LOWER(address) AS eth_address -- Use LOWER for consistent formatting and DISTINCT to get unique addresses
FROM
  `githubarchive.year.2024` t, -- Alias the table for clarity
  UNNEST(
    -- Use REGEXP_EXTRACT_ALL to find all occurrences matching the pattern
    REGEXP_EXTRACT_ALL(
      -- Concatenate the issue body and comment body to search in both
      -- Use COALESCE to handle cases where one or both might be NULL
      CONCAT(
        COALESCE(JSON_EXTRACT_SCALAR(t.payload, '$.issue.body'), ''),
        ' ', -- Add a space separator
        COALESCE(JSON_EXTRACT_SCALAR(t.payload, '$.comment.body'), '')
      ),
      -- Regular expression for an Ethereum address: '0x' followed by 40 hex characters
      r'0x[a-fA-F0-9]{40}'
    )
  ) AS address -- Alias the result of UNNEST
WHERE 1=1
  AND t.repo.name = 'LayerZero-Labs/sybil-report'
  AND t.type = "IssueCommentEvent"
)

SELECT
  eth_address,
  COUNT(*) AS hits
FROM base
GROUP BY 1
ORDER BY 2 DESC
```

This should [cover all of these](https://common.xyz/layerzero/search?q=sybil&communityScope=layerzero&sort=Best) lists:

- https://common.xyz/layerzero/discussion/18713-submission
- https://common.xyz/layerzero/discussion/22360-sybil-report-ruslan3
- https://common.xyz/layerzero/discussion/21787-sybil-hunting-report-ruslan2
- https://common.xyz/layerzero/discussion/18713-submission
- https://common.xyz/layerzero/discussion/20043
- https://common.xyz/layerzero/discussion/18712?comment=83274
- https://common.xyz/layerzero/discussion/19280
- https://common.xyz/layerzero/discussion/22086-cross-chain-sybil-addresses

The query is quite exspensive (around 15USD in BigQuery), so I'm not going to run it more than once.

There is also a [`lz_provisional_sybil_list` file that I got from a random tweet](https://x.com/airdropping_me/status/1802902567338553605).

## ZK LayerZero List

Found an interesting [google sheet](https://docs.google.com/spreadsheets/d/1UT8cQbRDSaBduGTcBO6zZKH_4n_02r_cSCl2FflvM14) [on the Common.xyz forums](https://common.xyz/layerzero/discussion/19787-report-on-sybil-clusters-based-on-mainnet-activity).
Also referenced on [Portex blog post](https://research.portexai.com/sybil-attacks-the-silent-killers-of-crypto-applications/).

Seems to correlate very well with the lables in our training set.

## Uniswap Verified Wallets

Got a list of non sybil addresses from Uniswap.

https://github.com/Uniswap/sybil-list/blob/master/verified.json

```python
import httpx

# Download the JSON file
response = httpx.get(
    "https://raw.githubusercontent.com/Uniswap/sybil-list/refs/heads/master/verified.json"
)
json_data = response.json()

data = []
for key, value in json_data.items():
    record = value.get("twitter", {}).copy()
    record["address"] = key.lower()
    data.append(record)

pl.from_records(data).write_csv("../data/external/uniswap_verified_wallets.csv")
```

Doesn't seems there are a lots of hits with the wallets we have in training.

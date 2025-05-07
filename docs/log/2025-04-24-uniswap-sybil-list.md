# Uniswap Sybil List

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

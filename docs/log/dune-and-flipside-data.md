# Dune and Flipside Data

Trying to download some data (labels and contract addresses) from Dune and Flipside.

## Dune

Seems is not possible to do it via the UI. Using the API via `dune-spice` does not work as it will scan more than the free limit.

I got a subset of the data but is not useful. Specially after adding the second batch of test addresses.

## Flipside

Using the Flipside API, I was able to query address labels and contract data for our dataset of 852475 addresses. The process involved:

1. Installing the Flipside Python client: `uv pip install -q flipside`
2. Setting up the API connection with my key
3. Processing addresses in batches of 100,000 to avoid API limits

For address labels, I used the Flipside client to run SQL queries against the `crosschain.core.address_labels` table and the `crosschain.core.contracts` table in batches.

Using these labels now instead of the ones from Dune.

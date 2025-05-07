# Coinbase Reputation API

Got an API key from Coinbase and installed `cdp-sdk-python` from the GitHub repo. The API is breaking on me with the following error: `AttributeError: 'NoneType' object has no attribute 'encode'`.

This is the code I'm running:

```python
import os
from cdp import *

api_key_name = os.getenv("CDP_API_KEY_NAME")
api_key_private_key = os.getenv("CDP_API_KEY_PRIVATE_KEY")

Cdp.configure(api_key_name, api_key_private_key)

external_address = Address("base-sepolia", "0xb9ecee9a0e273d8A1857F3B8EeA30e5dD3cb6335")

external_address.balance()
```

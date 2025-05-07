# LayerZero List from GitHub Archive

LayerZero [created a repository](https://github.com/LayerZero-Labs/sybil-report) (now deleted) for people to report or identify sybil addresses. The process, from what I can tell was to create issues with the addresses and some context or justification.

GitHub Archive has the data for the repo, so we cann get all the addresses from the issues and comments doing some fun SQL and regex magic.

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
  -- Optional: Add a LIMIT if you only want a sample of addresses
  -- LIMIT 1000
)

SELECT
  eth_address,
  COUNT(*) AS hits
FROM base
GROUP BY 1
ORDER BY 2 DESC
```

This should [cover these](https://common.xyz/layerzero/search?q=sybil&communityScope=layerzero&sort=Best) lists:

- https://common.xyz/layerzero/discussion/18713-submission
- https://common.xyz/layerzero/discussion/22360-sybil-report-ruslan3
- https://common.xyz/layerzero/discussion/21787-sybil-hunting-report-ruslan2
- https://common.xyz/layerzero/discussion/18713-submission
- https://common.xyz/layerzero/discussion/20043
- https://common.xyz/layerzero/discussion/18712?comment=83274
- https://common.xyz/layerzero/discussion/19280
- https://common.xyz/layerzero/discussion/22086-cross-chain-sybil-addresses

That said, not all are covered.

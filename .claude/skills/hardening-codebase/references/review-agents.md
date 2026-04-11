# Review Agent Prompts

Launch all three in parallel via the Agent tool. Pass the diff or file
list as context to each.

## Agent 1: Code Reuse

```
Review changed files for CODE REUSE issues.

For each change:
1. Search for existing utilities/helpers that could replace new code
2. Flag duplicate functionality across files
3. Flag inline logic that could use shared utilities

Focus on: repeated patterns, copy-pasted functions with slight
variation, fragile path computations that should be centralized.

Report: file, issue, suggested fix. No false positives.
```

## Agent 2: Code Quality

```
Review changed files for CODE QUALITY issues.

Look for:
1. Redundant state — duplicates existing state, could be derived
2. Parameter sprawl — adding params instead of restructuring
3. Copy-paste with variation — near-duplicate blocks to unify
4. Leaky abstractions — exposing internals, breaking boundaries
5. Stringly-typed code — raw strings where constants/enums exist
6. Logic bugs — off-by-one, unguarded None, silent fallthrough

Report: file, issue, suggested fix. Skip false positives.
```

## Agent 3: Efficiency

```
Review changed files for EFFICIENCY issues.

Look for:
1. Unnecessary work — redundant computations, repeated reads
2. Missed caching — same expensive result computed multiple times
3. Missed concurrency — independent ops run sequentially
4. N+1 patterns — loop of individual calls instead of batch
5. Overly broad operations — reading all when filtering for one
6. TOCTOU — pre-checking existence before operating

Report: file, issue, estimated savings. Skip false positives.
```

## Aggregation

After all three complete, deduplicate findings (agents often flag the
same issue from different angles). Rank by severity:

- **HIGH**: bugs, security, >50 lines of duplication
- **MEDIUM**: caching, DRY violations, magic strings
- **LOW**: minor inefficiency, style preferences

Present to user before fixing. Fix HIGHs and MEDIUMs only.

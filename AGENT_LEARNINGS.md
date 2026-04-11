# Agent Learnings

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves
- **Solution**: Implementation approach
- **References**: Related files

## Learned Patterns

### `make test` excludes hardware + network tests by default

- **Context**: When running, describing, or debugging `make test` / `make test_cov` behaviour
- **Problem**: The Makefile target reads as `uv run pytest $(PYTEST_QUIET)` with no visible marker filter — it looks like it runs every test. It does not. Any agent assuming `make test` runs all tests will be wrong.
- **Solution**: The exclusion lives in `pyproject.toml` under `[tool.pytest.ini_options]` as `addopts = "--strict-markers -m 'not hardware and not network'"`. To run the excluded tests explicitly: `uv run pytest -m hardware` or `uv run pytest -m network`.
- **References**: `pyproject.toml` (`[tool.pytest.ini_options]` section), `CONTRIBUTING.md` (command table + Hardware Tests section)

### Git log direction hazard — always use explicit `A..B` ranges

- **Context**: When assessing whether a branch is ahead of, behind, or diverged from main (or any other branch)
- **Problem**: `git log main --format='%h %s' -5` shows main's own recent history, NOT "commits on main not in the current branch". An earlier agent misread this output during the Phase 2 cleanup (2026-04-11) and confidently claimed main had advanced by 5 commits when it had not. That false reading would have driven a "branch-wins merge with orphan deletion" strategy that was completely unnecessary — the real state was "main at merge-base, branch strictly ahead".
- **Solution**: Always use explicit two-dot ranges: `git log HEAD..origin/main --oneline` (commits on main not in HEAD) and `git log origin/main..HEAD --oneline` (commits on branch not on main). Confirm divergence with `git merge-base origin/main HEAD` and compare against both heads. Never infer divergence from a one-sided `git log <branch> -N`.
- **References**: N/A (general git hygiene; applies to any branch comparison)

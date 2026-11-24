# Agent Learnings

## Template

- **Context**: When/where this applies
- **Problem**: What issue this solves
- **Solution**: Implementation approach
- **References**: Related files

## Learned Patterns

### Verify a doc's claim against code before repeating it — README claimed a module the table omitted

- **Context**: When any doc (README, architecture.md, roadmap.md) asserts that a module, flag, or capability exists, and that assertion is about to be repeated in a new doc, plan, issue, or PR body.
- **Problem**: README's Project Structure line names an "ELN" module in `src/so101/`. `docs/architecture.md` — the declared AUTHORITY for the module table — did not list one. Faced with that conflict an agent guessed three filenames (`eln.py`, `elabftw.py`, `eln/__init__.py`), found none, and concluded the module did not exist. It does: `src/so101/eln_client.py`, fully implemented and tested. The wrong conclusion was written into three files before being caught. Absence of a guessed filename is not absence of the feature.
- **Solution**: Resolve doc-vs-doc conflicts against **code**, and search by symbol/content rather than by guessed filename. `Bash ls`/`find`/`grep` are denylisted in `.claude/settings.json`, so use `python3 -c` with `os.walk` + `re`, or delegate to a subagent with search tools. Only report "does not exist" after a content search over `src/` and `tests/`, and state what was searched.
- **Same root cause, second form — subagent research summaries.** A research subagent reported "MCAP is Apache-2.0"; it is MIT (per `foxglove/mcap`'s own LICENSE). The claim was written into `docs/outlook-observability.md` and only caught on a later re-audit. A subagent's finding is a hypothesis, not a source. Before a vendor/license/pricing claim lands in any artifact, fetch the artifact itself — the LICENSE file, the pricing page, the package metadata — not a summary of it. `raw.githubusercontent.com/<org>/<repo>/main/LICENSE` settles licenses in one request; the GitHub API is rate-limited unauthenticated and `gh` may have no credentials, so prefer polyfetch (see `polyfetch-scrape/USING.md`) for JS-rendered vendor pages.
- **References**: `src/so101/eln_client.py`, `docs/architecture.md` (Module Responsibilities table), `README.md` (Project Structure), `docs/outlook-observability.md` (§ Sourcing and confidence)

### `make validate` did not gate docs — markdown and links were unchecked

- **Context**: Before pushing any change that touches `*.md`, `.lychee.toml`, or `.markdownlint.json`.
- **Problem**: `validate` was `lint check_types test_cov check_complexity` — Python only. A docs-only change passed the canonical gate green while markdown lint and link checking never ran. Both gates had silently drifted red on main (2 MD033 errors, 4 dead/blocked links) because nothing local ran them, even though CI checks them via the `lint-md-links.yml` reusable workflow.
- **Solution**: `validate` now also runs `check_docs` + `check_links`; `quick_validate` (`lint check_types`) remains the offline inner loop since `check_links` needs network. When a link fails, distinguish the two cases: a 403/400/timeout from bot protection belongs in `.lychee.toml`'s exclude list, but a **404 is real link rot** — excluding it hides a dead reference instead of fixing it.
- **References**: `Makefile` (`validate`, `quick_validate`), `.lychee.toml`, `.markdownlint.json`, `.github/workflows/lint-md-links.yml`

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

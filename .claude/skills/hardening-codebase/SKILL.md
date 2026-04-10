---
name: hardening-codebase
description: Audit and tighten codebase quality gates — lint, types, tests, code
  review. Use when onboarding a project, before a release, or when validation is
  too permissive.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
  argument-hint: "[scope: full | audit | tighten | review | fix]"
  stability: experimental
---

# Harden Codebase

**Scope**: $ARGUMENTS (default: full)

Systematic quality tightening. Seven phases, each with a clear gate.
KISS: tighten one level at a time — never jump to max strictness.

## Phase 1: AUDIT (read-only)

1. Does `make setup_all` (or equivalent) work from scratch?
2. What lint rules are enabled? Gap vs recommended?
   See `references/lint-tightening-checklist.md`
3. Type checker strictness level?
4. Do tests pass? Are slow/hardware tests filtered?
5. Is check-only gate separate from auto-fix?

**Gate**: Issue list ranked HIGH/MEDIUM/LOW. Present to user before
proceeding.

## Phase 2: TIGHTEN (config only — no code changes)

1. Enable next-level lint rules (baseline → recommended, not strict)
2. Bump type checker one level
3. Split auto-fix from check-only gate if missing
4. Add test marker filters for slow/hardware/network
5. Count new violations — report before fixing

**Gate**: Config committed. Violation count known.

## Phase 3: FIX (mechanical)

1. Run auto-fix
2. Fix remaining violations manually
3. Update tests broken by signature changes
4. `make validate` must pass

**Gate**: All checks green. Commit fixes.

## Phase 4: TEST OVERHAUL (meaningful tests only)

1. Classify every test: behavioral / implementation / trivial
2. Rewrite implementation tests as behavioral (assert outcomes, not internals)
3. Delete trivial tests that add no value
4. Add missing behavioral tests for error recovery, state transitions, edge cases
5. Add property-based tests (Hypothesis) for invariants
6. Add complexity gate (complexipy, max 15/function)
7. `make validate` must pass with coverage gate

**Gate**: All tests behavioral. Coverage ≥ 80%. Complexity ≤ 15.

## Phase 5: REVIEW (3 parallel agents)

Launch all three from `references/review-agents.md`:

- **Reuse**: duplication, missing shared helpers
- **Quality**: copy-paste, magic strings, abstractions, bugs
- **Efficiency**: unnecessary work, missed caching

**Gate**: Ranked findings presented to user.

## Phase 6: REFACTOR (apply findings)

1. Fix HIGH and MEDIUM only (80/20)
2. Skip LOW unless trivial
3. `make validate` after each fix
4. Commit by topic

**Gate**: All checks green. Findings addressed.

## Phase 7: SHIP

1. Push branch
2. Create PR with summary + test plan

## Scope shortcuts

- `audit` — Phase 1 only (read-only report)
- `tighten` — Phases 1-3 (config + fix)
- `tests` — Phase 4 only (test overhaul)
- `review` — Phase 5 only (3-agent review)
- `fix` — Phase 6 only (apply existing findings)
- `full` — All phases

## References

See `references/lint-tightening-checklist.md` for language-specific
rule progressions and `references/review-agents.md` for agent prompts.

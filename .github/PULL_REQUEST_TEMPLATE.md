# Summary

<!-- Brief description of what this PR does and why -->

Closes <!-- #issue-number or N/A -->

## Type of Change

<!-- Check all that apply. Commit type must match .gitmessage -->

- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `refactor` — no functional change
- [ ] `test` — test additions or fixes
- [ ] `ci` — CI/CD changes
- [ ] `build` — build system or dependency changes
- [ ] `chore` — tooling, config, maintenance
- [ ] **Breaking change** — add `!` after commit type

## Self-Review

- [ ] I have reviewed my own diff and removed debug/dead code
- [ ] Commit messages follow [`.gitmessage`](../.gitmessage) format

## Testing

- [ ] `make validate` passes (lint + type check + tests)
- [ ] New functionality has corresponding tests
- [ ] Hardware-dependent tests gated with `@pytest.mark.hardware`

## Documentation

- [ ] [`CHANGELOG.md`](../CHANGELOG.md) updated under `## [Unreleased]`
- [ ] Docstrings added/updated for new/modified functions
- [ ] `AGENT_LEARNINGS.md` updated if new pattern discovered

## Security

- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Serial command inputs validated
- [ ] WebSocket command inputs validated

# Contributing

Technical workflows and coding standards for so101-biolab-automation.
For AI agent behavioral rules, see [AGENTS.md](AGENTS.md).

## Instant Commands

| Command | Purpose |
|---------|---------|
| `make setup` | Install all dependencies |
| `make validate` | Complete pre-commit validation (lint + type check + test) |
| `make quick_validate` | Fast development validation (lint + type check) |
| `make test` | Run all non-hardware tests with pytest |
| `make calibrate` | Calibrate all arms |
| `make teleop` | Start teleoperation |
| `make record` | Record training episodes |
| `make train` | Train ACT policy |
| `make serve` | Start remote dashboard |

**Emergency fallback** (if make commands fail):
```bash
uv run ruff format . && uv run ruff check . --fix
uv run pyright
uv run pytest -m "not hardware"
```

## Testing Strategy

### Unit Tests (always required)
- Mock all hardware and external dependencies using `@patch`
- Test business logic and data validation
- Mirror `src/` structure in `tests/`

### Hardware Tests (opt-in)
- Tag with `@pytest.mark.hardware` — excluded from `make test` by default
- Run explicitly: `uv run pytest -m hardware`
- Require physical arms connected and calibrated

### BDD Approach
- Write tests first, implement code iteratively
- All tests must pass before advancing to the next step

## Code Style

- **Python 3.10+** with full type hints
- **Google-style docstrings** for all functions, classes, methods
- **Absolute imports** only (no relative imports)
- **Ruff** for formatting and linting, **pyright** for type checking
- **YAML configs** for all hardware-specific values — never hardcode ports, positions, or coordinates
- **LeRobot API** for all arm operations — never bypass the abstraction layer
- Coordinates in mm, SBS 96-well standard (A1 origin top-left, 9mm spacing)
- Add `# Reason:` comments for complex logic explaining the *why*

## Pre-commit Checklist

1. `make validate` — lint + type check + tests must all pass
2. Update `CHANGELOG.md` — add entry to `## [Unreleased]` section
3. Commit with conventional commit format (see `.gitmessage`)

## Conventional Commits

Types: `feat | fix | build | chore | ci | docs | style | refactor | perf | test`
Scopes: `biolab | dashboard | configs | scripts | tests | docs`

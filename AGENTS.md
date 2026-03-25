# Agent Instructions for so101-biolab-automation

Behavioral rules for AI agents working on dual SO-101 robotic arm bio-lab automation.
For technical workflows and coding standards, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Core Rules

- Follow SDLC principles: maintainability, modularity, reusability
- Use BDD approach for feature development
- **Never assume missing context** — ask if uncertain about requirements
- **Never hallucinate libraries** — only use packages verified in `pyproject.toml`
- **Always confirm file paths exist** before referencing in code or tests
- **Never delete existing code** unless explicitly instructed
- **Document new patterns** in AGENT_LEARNINGS.md (concise, laser-focused)
- **Request human feedback** in AGENT_REQUESTS.md when blocked

## Architecture Overview

- **Dual SO-101 arms** — leader/follower teleoperation and ACT policy execution
- **LeRobot** — arm control, imitation learning, teleoperation recording
- **PyLabRobot** — liquid handling abstractions (pipette, plate coords)
- **FastAPI dashboard** — remote oversight with WebSocket command channel

Key directories:
- `src/biolab/` — Core: arm control, pipette, plate coords, tool changer, safety monitor
- `src/dashboard/` — FastAPI + WebRTC remote oversight
- `configs/` — YAML for arm ports, plate layout, tool dock positions
- `scripts/` — Calibration, recording, training, demo wrappers

## Decision Framework

**Priority order:** User instructions → AGENTS.md → CONTRIBUTING.md → project patterns

**Information sources:**
- Requirements/scope: task description or user instruction (primary)
- Technical implementation: `src/` code + `configs/` (authority)
- Hardware details: `configs/*.yaml` (authority — never hardcode values from here)

**Anti-scope-creep:** Only implement what is explicitly requested. Hardware automation
is safety-critical — never add untested behaviour speculatively.

## Quality Thresholds

Before starting any task:
- **Context**: 8/10 — understand requirements, codebase patterns, hardware constraints
- **Clarity**: 7/10 — clear implementation path and expected outcomes
- **Alignment**: 8/10 — follows project patterns and hardware safety rules
- **Success**: 7/10 — confident in completing task correctly

If below threshold: gather more context or escalate to AGENT_REQUESTS.md.

## Agent Quick Reference

**Pre-task:**
- Read AGENTS.md → CONTRIBUTING.md
- Confirm quality thresholds met
- Check AGENT_LEARNINGS.md for prior art

**During task:**
- Use `make` commands (document deviations)
- Follow BDD: write tests first, implement iteratively
- Tag hardware tests with `@pytest.mark.hardware`

**Post-task:**
- Run `make validate` — must pass all checks
- Update CHANGELOG.md for non-trivial changes
- Document new patterns in AGENT_LEARNINGS.md
- Escalate to AGENT_REQUESTS.md if blocked

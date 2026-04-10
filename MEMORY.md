# Claude Code Memory

Cross-repo working patterns for AI coding agent workflows.

## Git Conventions

- **Protected mains** — always feature branches + PRs
- **Squash merge**: `PR <conventional-commit-title> (#NUM)`, branch commits in body
- **Push**: `git push origin <branch-name>` (never `HEAD` or bare)

## Auth & Credentials

<!-- Project-specific auth patterns (PATs, tokens, SSO) -->

## Sandbox & Settings

- Network sandbox ON, filesystem relaxed (container isolation)
- SOT: `~/.claude/settings.json`
- Settings require session restart (no hot-reload)

## Project Patterns

<!-- Project-specific conventions, architecture notes -->

## Learned Preferences

<!-- Agent behavior corrections, confirmed approaches -->

## Known Issues

<!-- Active workarounds, known bugs, environment quirks -->

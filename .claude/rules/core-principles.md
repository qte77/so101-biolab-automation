# Core Principles

**MANDATORY for ALL tasks.**

## User-Centric

**Safety, Reliability, User Success** — Every decision optimizes for safe robot
operation, system reliability, and clear user outcomes.

## Code Quality

**KISS** — Simplest solution that works. Clear > clever. Especially critical for
hardware control code where complexity causes failures.

**DRY** — Single source of truth. Reference, don't duplicate. One config per
robot parameter.

**YAGNI** — Implement only what's requested. No speculative features in
safety-critical paths.

## Execution

**Concise and Focused** — Minimal code for the task. Touch only task-related code.

**Reuse and Extend** — Use existing patterns and dependencies. Don't rebuild.

**Prevent Incoherence** — Validate against existing hardware configs and robot specs.

## Pre-Task Checklist

- [ ] Does this serve user/safety value?
- [ ] Is this the simplest approach?
- [ ] Am I duplicating existing work?
- [ ] Do I actually need this?
- [ ] Am I touching only relevant code?

## Post-Task Review

- **Did we forget anything?** Check requirements thoroughly.
- **High-ROI enhancements?** Suggest opportunities (don't implement).
- **Something to delete?** Remove obsolete or unnecessary code.

**IMPORTANT**: Do NOT alter files based on this review. Only output suggestions.

## When in Doubt

**STOP. Ask the user.**

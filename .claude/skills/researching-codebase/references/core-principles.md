# Core Principles

**MANDATORY for ALL tasks.** These principles override all other guidance when
conflicts arise.

## User-Centric Principles

**User Experience, User Joy, User Success** - Every decision optimizes for
user value, clarity, and usability.

## Code Quality Principles

**KISS (Keep It Simple, Stupid)** - Simplest solution that works. Clear > clever.

**DRY (Don't Repeat Yourself)** - Single source of truth. Reference, don't duplicate.

**YAGNI (You Aren't Gonna Need It)** - Implement only what's requested. No
speculative features.

## Execution Principles

**Concise and Focused** - Minimal code/text for task. Touch only task-related code.

**Reuse and Extend** - Use existing patterns and dependencies. Don't rebuild.

**Prevent Incoherence** - Spot inconsistencies. Validate against existing patterns.

**Resolve Ambiguity** - Clarify vague requirements before acting.

## Decision Principles

**Rigor and Sufficiency** - Research enough to decide confidently. No more, no less.

**High-Impact Quick Wins** - Prioritize must-do tasks. Ship fast, iterate.

**Actionable and Concrete** - Specific deliverables. Measurable outcomes.

**Root-Cause and First-Principles** - Understand the "why". Solve root problems.

## Before Starting Any Task

- [ ] Does this serve user value?
- [ ] Is this the simplest approach?
- [ ] Am I duplicating existing work?
- [ ] Do I actually need this?
- [ ] Am I touching only relevant code?
- [ ] What's the root cause I'm solving?

## Post-Task Review

Before finishing, ask yourself:

- **Did we forget anything?** - Check requirements thoroughly
- **High-ROI enhancements?** - Suggest opportunities (don't implement)
- **Something to delete?** - Remove obsolete/unnecessary code

**IMPORTANT**: Do NOT alter files based on this review. Only output
suggestions to the user.

## When in Doubt

**STOP. Ask the user.**

Don't assume, don't over-engineer, don't add complexity.

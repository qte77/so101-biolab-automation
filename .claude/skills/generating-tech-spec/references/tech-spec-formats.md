---
title: Technical Specification Formats
description: >-
  Templates for ADR (MADR), RFC, design document, and
  proposal document types
created: 2026-03-01
category: templates
version: 1.0.0
---

# Technical Specification Formats

## ADR — Architectural Decision Record (MADR)

Based on [MADR](https://adr.github.io/madr/) (Markdown Any Decision Records).

```markdown
---
title: <Short title of the decision>
date: YYYY-MM-DD
status: proposed | accepted | deprecated | superseded
superseded-by: NNNN (if applicable)
---

# NNNN — <Title>

## Context and Problem Statement

<Describe the context and the problem or requirement that motivates this decision.>

## Decision Drivers

- <Driver 1>
- <Driver 2>

## Considered Options

1. <Option 1>
2. <Option 2>
3. <Option 3>

## Decision Outcome

Chosen option: "<Option N>", because <justification>.

### Positive Consequences

- <Consequence 1>

### Negative Consequences

- <Consequence 1>

## Pros and Cons of the Options

### Option 1: <Name>

- Good, because <argument>
- Bad, because <argument>

### Option 2: <Name>

...

## More Information

<Links to related ADRs, issues, or documents.>
```

## RFC — Request for Comments

```markdown
---
title: <RFC title>
rfc: NNNN
date: YYYY-MM-DD
author: <Name>
status: draft | proposed | accepted | rejected | withdrawn
---

# RFC NNNN — <Title>

## Summary

<One paragraph summary of the proposal.>

## Motivation

<Why is this change needed? What problem does it solve?>

## Detailed Design

<Technical details of the proposal. Include:>

### API Changes

<If applicable, show before/after.>

### Data Model Changes

<If applicable, show schema changes.>

### Migration Path

<How do we get from current state to proposed state?>

## Drawbacks

<Why should we NOT do this?>

## Alternatives Considered

<What other approaches were considered and why were they rejected?>

## Unresolved Questions

<What aspects of the design are still to be determined?>

## Implementation Plan

- [ ] Step 1
- [ ] Step 2
```

## Design Document

```markdown
---
title: <Design document title>
date: YYYY-MM-DD
author: <Name>
status: draft | in-review | approved | implemented
reviewers: <Comma-separated names>
---

# <Title>

## Overview

<1-2 paragraph summary of what this document covers and why.>

## Goals and Non-Goals

### Goals

- <Goal 1>

### Non-Goals

- <Non-goal 1>

## Background

<Context, prior art, and relevant history.>

## Design

### Architecture

<High-level architecture description. Include diagrams if helpful.>

### Components

<Detailed description of each component.>

### Data Flow

<How data moves through the system.>

### Error Handling

<How errors are handled, retried, and surfaced.>

## Security Considerations

<Authentication, authorization, data privacy.>

## Testing Strategy

<How will this be tested? Unit, integration, E2E.>

## Rollout Plan

<Phased rollout, feature flags, rollback strategy.>

## Open Questions

<Unresolved design decisions.>
```

## Proposal

```markdown
---
title: <Proposal title>
date: YYYY-MM-DD
author: <Name>
status: draft | submitted | approved | rejected
---

# <Title>

## Executive Summary

<2-3 sentence summary of the proposal and expected outcome.>

## Problem Statement

<Clear description of the problem being solved.>

## Proposed Solution

<Detailed description of the proposed approach.>

## Scope

### In Scope

- <Item 1>

### Out of Scope

- <Item 1>

## Success Criteria

<How will we measure success?>

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| <Risk 1> | High/Med/Low | High/Med/Low | <Mitigation> |

## Dependencies

<External dependencies, team dependencies, prerequisite work.>

## Next Steps

- [ ] Step 1
- [ ] Step 2
```

## References

- [MADR — Markdown Any Decision Records](https://adr.github.io/madr/)
- [Rust RFC process](https://github.com/rust-lang/rfcs)
- [Google Design Docs](https://www.industrialempathy.com/posts/design-docs-at-google/)

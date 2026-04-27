---
title: Testing Strategy
version: 1.0
applies-to: Agents and humans
purpose: High-level testing strategy aligned with KISS/DRY/YAGNI
see-also: tdd-best-practices.md
---

# Testing Strategy

**Purpose**: What to test, test organization, mocking strategy,
decision checklist. Language-agnostic.

## Core Principles

| Principle | Testing Application |
|-----------|---------------------|
| **KISS**  | Test behavior, not implementation details |
| **DRY**   | No duplicate coverage across tests |
| **YAGNI** | Don't test library behavior |

## What to Test

**High-Value** (test these):

1. Business logic — core algorithms, calculations, decision rules
2. Integration points — API handling, external service interactions
3. Edge cases with real impact — empty inputs, error propagation,
   boundary conditions
4. Contracts — API response formats, data transformations

**Low-Value** (avoid these):

1. Library behavior — framework validation, runtime internals
2. Trivial assertions — `x is not null`, `typeof x === "object"`
3. Default values — unless defaults encode business rules
4. Documentation content — string-contains checks

### Patterns to Remove

| Pattern | Why Remove | Example |
|---------|------------|---------|
| Import/existence | Runtime handles | `test module exports foo` |
| Field existence | Type system validates | `test model has field x` |
| Default constants | Testing `300 === 300` | `assert DEFAULT === 300` |
| Over-granular | Consolidate to schema | 8 tests for one model |
| Type checks | Type checker handles | `assert result instanceof Object` |
| Stale mocks | Patches removed interfaces | `mock("module.deleted_name")` |

**Rule**: If the test wouldn't catch a real bug, remove it.

## Test Levels: Unit vs Integration

**Unit Tests**:
- Test single component in isolation
- Fast execution (<10ms per test)
- No external dependencies (databases, APIs, file I/O)
- Use mocks/fakes for dependencies

**Integration Tests**:
- Test multiple components working together
- May involve I/O (slower execution)
- Use real or in-memory services
- Validate component interactions

## Mocking Strategy

**When to use mocks**:
- External APIs you don't control (payment gateways, third-party)
- Slow operations (file I/O, network calls) in unit tests
- Non-deterministic dependencies (time, random, UUIDs)
- Error scenarios hard to reproduce (network timeouts, rate limits)

**When to use real services**:
- In-memory alternatives exist (SQLite for DB, etc.)
- Integration tests validating actual behavior
- Your own services/components (test real interactions)

**Mock safety rules**:
- Constrain mocks to real interfaces (typed mocks, spec=)
- Bare untyped mocks accept any method silently — dangerous
- Update mocks when interfaces change

## Test Organization

**Flat structure** (small projects):

```text
tests/
├── *.test.*           # Unit tests
└── setup.*            # Shared setup
```text

**Organized structure** (larger projects):

```text
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Multi-component tests
└── setup.*            # Shared setup
```

## Naming Conventions

Name describes behavior, not method:

```text
// Unit tests
"calculates total from items"
"returns empty array for unknown user"
"throws on invalid input"

// Integration tests
"saves order to database and retrieves it"
"sends notification after payment"
```

## Priority Test Areas

1. **Core business logic** — algorithms, calculations, rules (unit)
2. **Contracts** — request/response formats, data shapes (unit + integration)
3. **Edge cases** — empty/null inputs, boundaries (unit)
4. **Integration points** — external services, data stores (integration)

## Decision Checklist

Before writing a test:

1. Does this test **behavior** (keep) or **implementation** (skip)?
2. Would this catch a **real bug** (keep) or is it **trivial** (skip)?
3. Is this testing **our code** (keep) or **a library** (skip)?

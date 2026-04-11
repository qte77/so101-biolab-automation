---
title: TDD Best Practices
version: 1.0
based-on: Industry research 2025-2026, adapted from python-dev testing-python
see-also: testing-strategy.md
---

**Purpose**: How to do TDD — Red-Green-Refactor cycle, AAA structure,
best practices, anti-patterns. Language-agnostic.

## The Red-Green-Refactor Cycle

```text
┌─────────────┐
│  1. RED     │  Write a failing test
│             │  (test what should happen)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  2. GREEN   │  Write minimal code to pass
│             │  (make it work)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  3. REFACTOR│  Improve code quality
│             │  (make it clean)
└─────┬───────┘
      │
      └──────> Repeat
```

## Core Practices

### 1. Write Tests First

**Why**: Enforces modular, decoupled code with clear interfaces.

Write the test that describes expected behavior. Then implement
minimal code to make it pass. Not the other way around.

### 2. Use Arrange-Act-Assert (AAA)

Structure every test in three phases:

```
// ARRANGE — Set up test data
items = [{ price: 10, qty: 2 }, { price: 5, qty: 1 }]
processor = new OrderProcessor()

// ACT — Execute the behavior
total = processor.calculateTotal(items)

// ASSERT — Verify the outcome
assertEqual(total, 25)
```

### 3. Keep Tests Atomic and Isolated

**One behavior per test.** A test for addition doesn't also test
subtraction. Each test is independent — no shared mutable state.

### 4. Test Edge Cases Before Happy Paths

Cover failure modes first (empty input, malformed data, nulls,
boundaries), then success cases.

### 5. Descriptive Test Names

Name describes behavior:
- Good: `"returns 404 for unknown user"`
- Bad: `"test service response"`

## Benefits of TDD

- **Design quality**: Forces modular, testable code
- **Fast feedback**: Catches bugs while context is fresh
- **Refactoring confidence**: Tests enable safe improvements
- **Living documentation**: Tests describe how the system behaves
- **Defect reduction**: Studies show 40-90% reduction in defect density

## Anti-Patterns

### Testing implementation details

```
// BAD — Tests internal structure
assert(service._internalClient instanceof SomeLibrary)

// GOOD — Tests behavior
assertEqual(service.fetch("key"), expectedValue)
```

### Untyped mocks

Bare mocks that accept any method silently mask API drift.
Always constrain mocks to the real interface.

### Overly complex tests

If test setup is harder to understand than the code under test,
simplify. Avoid excessive mocking.

### Chasing 100% coverage

Aim for meaningful behavior coverage, not line coverage percentage.

### Stale mocks/patches

When source code changes (renamed imports, restructured modules),
update or delete tests that reference the old interface.

## When to Use TDD

**Use TDD for**:
- Business logic (calculations, algorithms, rules)
- Data transformations (model conversions, parsing)
- Edge case handling (empty inputs, nulls, boundaries)
- API endpoints (request/response validation)
- Component behavior (renders, callbacks, state changes)

**Consider alternatives for**:
- Simple CRUD operations
- UI layouts and styling (use visual testing)
- Exploratory prototypes (add tests after direction is clear)

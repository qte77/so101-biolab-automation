---
title: Testing Strategy
version: 6.0.0
applies-to: Agents and humans
purpose: High-level testing strategy aligned with KISS/DRY/YAGNI
see-also: tdd-best-practices.md, bdd-best-practices.md
---

**Purpose**: Python-specific testing tools and when to use each.

> Language-agnostic testing strategy (what to test, mocking, organization)
> is in the `tdd-core` plugin. This file extends it with Python tools
> (pytest, Hypothesis, inline-snapshot, pytest-bdd).

## Core Principles

| Principle | Testing Application |
| ----------- | --------------------- |
| **KISS** | Test behavior, not implementation details |
| **DRY** | No duplicate coverage across tests |
| **YAGNI** | Don't test library behavior (Pydantic, FastAPI, etc.) |

## What to Test

**High-Value** (Test these):

1. Business logic - Core algorithms, calculations, decision rules
2. Integration points - API handling, external service interactions
3. Edge cases with real impact - Empty inputs, error propagation,
   boundary conditions
4. Contracts - API response formats, model transformations

**Low-Value** (Avoid these):

1. Library behavior - Pydantic validation, `os.environ` reading,
   framework internals
2. Trivial assertions - `x is not None`, `isinstance(x, SomeClass)`,
   `hasattr()`, `callable()`
3. Default values - Unless defaults encode business rules
4. Documentation content - String contains checks

### Patterns to Remove (Test Suite Optimization)

| Pattern | Why Remove | Example |
| --------- | ------------ | --------- |
| Import/existence | Python/imports handle | `test_module_exists()` |
| Field existence | Pydantic validates | `test_model_has_field_x()` |
| Default constants | Testing `300 == 300` | `assert DEFAULT == 300` |
| Over-granular | Consolidate to schema | 8 tests for one model |
| Type checks | pyright handles | `assert isinstance(r, dict)` |
| Filesystem leak | Writes mock data to real paths | `cache_dir` not redirected to `tmp_path` |
| Stale fixture patches | Patches removed imports, pollutes other tests | `patch("module.deleted_name")` |

**Rule**: If the test wouldn't catch a real bug, remove it.

## Testing Approach

### Tool Selection Guide

Each tool answers a different testing question. Pick the right one:

| Tool | Question it answers | Input | Output assertion | Use for |
| --- | --- | --- | --- | --- |
| **pytest** | Does this logic produce the right result? | Known, specific | Manual `assert` | TDD, unit tests, integration tests |
| **Hypothesis** | Does this hold for ALL inputs? | Generated, random | Property invariants | Edge cases, math, parsers |
| **inline-snapshot** | Does this output still look the same? | Known, specific | Auto-captured structure | Regression, contracts, model dumps |
| **pytest-bdd** | Does this meet acceptance criteria? | Scenario-driven | Given-When-Then | Stakeholder validation |

**One-line rule**: pytest for **logic**, Hypothesis for
**properties**, inline-snapshot for **structure**,
pytest-bdd for **behavior specs**.

### TDD with pytest + Hypothesis (Primary)

**Primary methodology**: Test-Driven Development (TDD)

**Tools** (see `tdd-best-practices.md`):

- **pytest**: Core tool for all TDD tests (specific test cases)
- **Hypothesis**: Extension for property-based edge case testing
  (generative tests)

**When to use each**:

- **pytest**: Known cases (specific inputs, API contracts,
  known edge cases)
- **Hypothesis**: Unknown edge cases (any string, any number,
  invariants for ALL inputs)

### Hypothesis Test Priorities (Edge Cases within TDD)

| Priority | Area | Why | Example |
| ---------- | ------ | ----- | --------- |
| **CRITICAL** | Math formulas | All inputs work | `test_score_bounds()` |
| **CRITICAL** | Loop termination | Always terminates | `test_terminates()` |
| **HIGH** | Input validation | Arbitrary text ok | `test_parser_safe()` |
| **HIGH** | Serialization | Valid JSON always | `test_output_valid()` |
| **MEDIUM** | Invariant sums | Total equals sum | `test_total_sum()` |

See [Hypothesis documentation](https://hypothesis.readthedocs.io/) for
usage patterns.

### Inline Snapshots: Regression & Contract Tests (Supplementary)

**inline-snapshot** auto-captures complex output structures directly
in test source code. It complements TDD — it does not replace it.

**When to use**:

- Pydantic `.model_dump()` output (full structure, auto-maintained)
- Complex return dicts (nested structures, parser outputs)
- Format conversion results (serialization, transformations)
- Integration results (multi-field response objects)

**When NOT to use**:

- TDD Red-Green-Refactor (snapshots can't fail before code exists)
- Hypothesis property tests (random inputs produce varying output)
- Simple value checks (`assert score >= 0.85`)
- Range/bound assertions (`0.0 <= x <= 1.0`)
- Relative comparisons (`assert a < b`)

```python
from inline_snapshot import snapshot

# REGRESSION - Capture full structure, auto-update on changes
def test_user_serialization():
    user = create_user(name="Alice", role="admin")
    assert user.model_dump() == snapshot()
    # pytest --inline-snapshot=create  → fills snapshot
    # pytest --inline-snapshot=fix     → updates when model changes

# NON-DETERMINISTIC VALUES - Use dirty-equals for dynamic fields
from dirty_equals import IsDatetime
def test_result_with_timestamp():
    result = process(input_data)
    assert result.model_dump() == snapshot({
        "score": 0.85,
        "timestamp": IsDatetime(),  # Not managed by snapshot
    })
```

**Commands**:

- `pytest --inline-snapshot=create` - Fill empty `snapshot()` calls
- `pytest --inline-snapshot=fix` - Update changed snapshots
- `pytest --inline-snapshot=review` - Interactive review mode

**Constraint**: Standard `pytest` runs validate snapshots normally.
No changes needed to `make validate` or CI.

### BDD: Stakeholder Collaboration (Optional)

**BDD** (see `bdd-best-practices.md`) - Different approach from TDD:

- **TDD**: Developer-driven, Red-Green-Refactor, all test levels
- **BDD**: Stakeholder-driven, Given-When-Then, acceptance criteria
  in plain language

**When to use BDD**:

- User-facing features requiring stakeholder validation
- Complex acceptance criteria needing plain-language documentation
- Collaboration between technical and non-technical team members

### Test Levels: Unit vs Integration

**Unit Tests**:

- Test single component in isolation
- Fast execution (<10ms per test)
- No external dependencies (databases, APIs, file I/O)
- Use mocks/fakes for dependencies
- Most common TDD use case

**Integration Tests**:

- Test multiple components working together
- Slower execution (may involve I/O)
- Use real or in-memory services
- Validate component interactions
- Fewer tests, broader coverage

**When to use each**:

```python
# UNIT TEST - Component in isolation
def test_order_calculator_computes_total():
    calculator = OrderCalculator()
    items = [Item(10), Item(15)]
    assert calculator.total(items) == 25  # Pure logic, no I/O

# INTEGRATION TEST - Components + external service
async def test_order_service_saves_to_database(db_session):
    service = OrderService(db_session)  # Real or in-memory DB
    order = await service.create_order(items=[Item(10)])
    saved = await service.get_order(order.id)
    assert saved.total == 10  # Tests service + DB interaction
```

### Mocking Strategy

**When to use mocks**:

- ✅ External APIs you don't control (payment gateways, third-party services)
- ✅ Slow operations (file I/O, network calls) in unit tests
- ✅ Non-deterministic dependencies (time, random, UUIDs)
- ✅ Error scenarios hard to reproduce (network timeouts, API rate limits)

**When to use real services**:

- ✅ In-memory alternatives exist (SQLite for PostgreSQL, Redis mock)
- ✅ Integration tests validating actual behavior
- ✅ Your own services/components (test real interactions)
- ✅ Testing the integration itself (verifying protocols, serialization)

**Mocking libraries**:

- `unittest.mock` - Standard library, use `patch()` and `MagicMock`
- `pytest-mock` - Pytest fixtures for mocking
- `responses` - Mock HTTP requests
- `freezegun` - Mock time/dates

**Mock safety rules**:

- Use `spec=RealClass` or `spec_set=RealClass` when mocking third-party return types
- Bare `MagicMock()` accepts any attribute name silently — use `spec=` to constrain to the real interface

```python
# MOCK external API
from unittest.mock import patch

def test_payment_processor_handles_api_failure():
    with patch('stripe.Charge.create') as mock_charge:
        mock_charge.side_effect = stripe.APIError("Rate limited")
        processor = PaymentProcessor()
        result = processor.charge(100)
        assert result.status == "failed"

# REAL service (in-memory)
def test_order_repository_saves_order(tmp_path):
    db = SQLite(":memory:")  # Real SQLite, in-memory
    repo = OrderRepository(db)
    order = repo.save(Order(total=100))
    assert repo.get(order.id).total == 100
```

### Priority Test Areas

1. **Core business logic** - Algorithms, calculations, decision rules
   (unit tests)
2. **API contracts** - Request/response formats, protocol handling
   (unit + integration)
3. **Edge cases** - Empty/null inputs, boundary values,
   numeric stability (unit with Hypothesis)
4. **Integration points** - External services, database operations
   (integration tests)

## Test Organization

**Flat structure** (small projects):

```text
tests/
├── test_*.py             # TDD unit tests
└── conftest.py           # Shared fixtures
```

**Organized structure** (larger projects):

```text
tests/
├── unit/                  # TDD unit tests (pytest)
│   ├── test_services.py
│   └── test_models.py
├── properties/            # Property tests (hypothesis)
│   ├── test_math_props.py
│   └── test_validation_props.py
├── acceptance/            # BDD scenarios (optional)
│   ├── features/*.feature
│   └── step_defs/
└── conftest.py           # Shared fixtures
```

## Running Tests

See the project's CONTRIBUTING.md for all make recipes and test commands.

## Naming Conventions

**Format**: `test_{module}_{component}_{behavior}`

```python
# Unit tests
test_user_service_creates_new_user()
test_order_processor_validates_items()

# Property tests
test_score_always_in_bounds()
test_percentile_ordering()
```

**Benefits**: Clear ownership, easier filtering (`pytest -k test_user_`),
better organization

## Decision Checklist

Before writing a test, ask:

1. Does this test **behavior** (keep) or **implementation** (skip)?
2. Would this catch a **real bug** (keep) or is it **trivial** (skip)?
3. Is this testing **our code** (keep) or **a library** (skip)?
4. Which tool:
   - **pytest** (default) - Unit tests, business logic, known edge cases
   - **Hypothesis** - Unknown edge cases (any input), numeric invariants
   - **inline-snapshot** - Complex output structures, model dumps, contracts
   - **pytest-bdd** (optional) - Acceptance criteria, stakeholder communication

## References

- TDD practices: `tdd-best-practices.md`
- BDD practices: `bdd-best-practices.md`
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [inline-snapshot Documentation](https://15r10nk.github.io/inline-snapshot/)

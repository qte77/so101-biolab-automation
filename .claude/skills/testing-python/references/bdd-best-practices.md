---
title: BDD Best Practices
version: 2.0
based-on: Industry research 2025-2026
see-also: testing-strategy.md, tdd-best-practices.md
---

**Purpose**: How to do BDD - Given-When-Then scenarios
for stakeholder collaboration on acceptance criteria.

## Behavior-Driven Development (BDD)

**BDD is NOT a superset of TDD** - they are different
methodologies with different focus.

**Key Distinction**:

- **TDD**: Developer-driven (Red-Green-Refactor) -
  unit, integration, and acceptance levels
- **BDD**: Stakeholder-driven
  (Discovery - Formulation - Automation) -
  acceptance criteria in plain language

**Relationship**: Both can test the same system. TDD
focuses on code correctness, BDD focuses on
stakeholder-defined behavior. You can USE TDD to
implement code that makes BDD scenarios pass.

BDD defines expected system behavior through
collaboration between technical and non-technical
stakeholders using plain-language scenarios.

## The Three Pillars

**1. Discovery**: Product Owner, Developer, Tester
collaborate to uncover concrete examples before
implementation.

**2. Formulation**: Capture examples as
Given-When-Then scenarios in business language.

**3. Automation**: Implement scenarios as executable
tests (living documentation).

## Given-When-Then Structure

**Format**: Gherkin syntax for scenarios

```gherkin
Feature: User Authentication
  As a registered user
  I want to log into my account
  So that I can access my dashboard

  Scenario: Successful login with valid credentials
    Given a registered user with email "alice@example.com"
      And a valid password "secure123"
    When the user submits the login form
    Then they should be redirected to the dashboard
      And they should see a welcome message
```

**Structure**:

- **Given** - Context and preconditions
- **When** - Action or event
- **Then** - Expected outcome

## Pillar 3: Automation

**Implement scenarios as executable tests**:

```python
from pytest_bdd import scenario, given, when, then

@scenario('features/auth.feature', 'Successful login with valid credentials')
def test_successful_login():
    pass

@given('a registered user with email "alice@example.com"')
def registered_user():
    return User(email="alice@example.com")

@when('the user submits the login form')
def submit_login(registered_user):
    return auth_service.login(registered_user.email, "secure123")

@then('they should be redirected to the dashboard')
def verify_redirect(submit_login):
    assert submit_login.redirect_url == "/dashboard"
```

**Benefits**:

- Living documentation that stays current
- Business-readable test reports
- Fast feedback on behavior changes

## Core BDD Practices

### 1. Collaboration First

**Shift focus from code to behavior**:

- Use plain-English descriptions
- All stakeholders can understand
- Align on requirements before implementation

**Three Amigos pattern**: PO defines "what", Dev
designs "how", Tester asks "what about...?"

### 2. Scenario Quality

Focus on business behavior, not implementation:

```gherkin
Scenario: Calculate order discount
  Given a customer with premium membership
  When they place an order over $100
  Then they should receive a 15% discount
```

Avoid technical details (database connections,
method names, data types).

### 3. Declarative, Not Imperative

State what (declarative):
"Given a user is authenticated"

Not how (imperative):
"Given user opens login, enters email,
enters password, clicks button..."

### 4. One Scenario Per Behavior

Each scenario tests one behavior. Avoid kitchen-sink
scenarios testing "all order features".

### 5. Maintain Scenarios

Revisit when requirements change, remove obsolete
scenarios.

- Prevent test suite bloat
- Keep scenarios aligned with business needs

## BDD Anti-Patterns

**Too technical**:

```gherkin
# BAD
Given the database has a record with id=123
When the API endpoint /api/v1/users/123 receives a GET request
Then the response JSON should have a "data" key
```

**Too many scenarios**:

- Keep scenarios focused
- Avoid testing every permutation
- Use Scenario Outlines for data variations

**Coupling to UI**:

```gherkin
# BAD - Brittle UI coupling
When I click the button with id "submit-btn"

# GOOD - Behavior focused
When I submit the order
```

## Combining TDD + BDD

BDD and TDD are different methodologies that can
work together:

- **BDD**: Defines acceptance criteria in
  stakeholder language (Given-When-Then)
- **TDD**: Implements components using
  Red-Green-Refactor cycle

**Strategy**: Write BDD scenario, use TDD to
implement components, BDD scenario passes.

See `testing-strategy.md` for detailed comparison.

## Tools for BDD

**Python ecosystem**:

- **pytest-bdd** - Gherkin scenarios with pytest
- **behave** - Pure BDD framework
- **Cucumber** - Cross-language BDD

See `pyproject.toml` for installed BDD tools.

**Run BDD scenarios**: See the project's CONTRIBUTING.md
for make recipes. Run BDD scenarios with
`uv run pytest tests/acceptance/`.

## When to Use BDD

**Use BDD for**:

- User-facing features
- Acceptance criteria
- Cross-team communication
- Integration tests
- API contracts

**Consider alternatives for**:

- Unit tests (use TDD)
- Performance tests

**Store scenarios in**: `tests/acceptance/features/`

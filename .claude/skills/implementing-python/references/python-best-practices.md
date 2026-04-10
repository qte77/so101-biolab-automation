---
title: Python Best Practices Reference
version: 2.0
applies-to: Agents and humans
purpose: Security-first Python coding standards with type safety and testing patterns
see-also: testing-strategy.md, tdd-best-practices.md
---

## Security (Non-Negotiable)

### Secrets Management

Load credentials from environment variables using Pydantic BaseSettings:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppEnv(BaseSettings):
    """Load secrets from environment variables."""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

config = AppEnv()
api_key = config.OPENAI_API_KEY
```

Never hardcode credentials in source code.

### Input Validation

Validate all external input immediately with Pydantic:

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    """Validate external input at system boundaries."""
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., ge=0, le=150)
    query: str = Field(..., min_length=1, max_length=1000)
```

### SQL Injection Prevention

Always use parameterized queries:

```python
from sqlalchemy import text

query = text("SELECT * FROM users WHERE id = :user_id")
result = connection.execute(query, {"user_id": user_id})
```

Never concatenate SQL strings with user input.

### Safe Deserialization

```python
import yaml

# Use SafeLoader for YAML
with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
```

Never deserialize untrusted data with unsafe methods (arbitrary code execution risk).

## Type Annotations

Use modern Python 3.10+ syntax for all function signatures:

```python
def process_data(
    items: list[dict[str, str]],
    count: int | None = None
) -> dict[str, int]:
    """Process items and return statistics."""
    ...
```

Key patterns:

- `str | None` instead of `Optional[str]`
- `list[str]` instead of `List[str]`
- Always annotate function parameters and return types
- Use `from __future__ import annotations` for forward references

## Pydantic Models

### When to Use Validation

Use `model_validate()` for external/untrusted data at system boundaries:

- API requests/responses
- File I/O (JSON/YAML/TOML)
- Cross-module boundaries with untrusted sources
- User input (CLI, forms, uploads)

Use direct construction for internal trusted data (same module).

### Model Definition

```python
from pydantic import BaseModel, Field, field_validator

class EvalRequest(BaseModel):
    """Request for agent evaluation."""

    model_config = {"strict": True, "frozen": True}

    agent_url: str = Field(..., description="URL of agent to evaluate")
    task: str = Field(..., description="Task description")

    @field_validator("task")
    def validate_task(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Task must be at least 10 characters")
        return v
```

### Validation at Boundaries

```python
from pydantic import ValidationError

# Validate external API response
try:
    response_data = await client.post(url, json=payload)
    result = EvaluationResult.model_validate(response_data.json())
except ValidationError as e:
    raise ValueError(f"Invalid response: {e.errors()}") from e

# Direct construction for internal trusted data
def _internal_process(data: InputData) -> ProcessedResult:
    return ProcessedResult(score=0.95, valid=True)
```

## Error Handling

### Error Message Factory Pattern

Create reusable error message functions:

```python
# src/app/utils/error_messages.py
from pathlib import Path

def file_not_found(file_path: str | Path) -> str:
    return f"File not found: {file_path}"

def invalid_json(error: str) -> str:
    return f"Invalid JSON: {error}"

def api_connection_error(error: str) -> str:
    return f"API connection error: {error}"
```

### Exception Handling

```python
import json
from app.utils.error_messages import file_not_found, invalid_json
from app.utils.log import logger

try:
    with open(config_path) as f:
        config_data = json.load(f)
except FileNotFoundError as e:
    msg = file_not_found(config_path)
    logger.error(msg)
    raise FileNotFoundError(msg) from e  # Chain exceptions
except json.JSONDecodeError as e:
    msg = invalid_json(str(e))
    logger.error(msg)
    raise json.JSONDecodeError(msg, str(config_path), 0) from e
```

Never use bare `except:` (catches SystemExit, KeyboardInterrupt).

## Logging

Configure Loguru for structured logging:

```python
from loguru import logger
from app.config.config_app import LOGS_PATH

logger.add(
    f"{LOGS_PATH}/{{time}}.log",
    rotation="1 MB",
    retention="7 days",
    compression="zip",
)

# Usage
logger.info("Processing started")
logger.error(f"Failed to process {item_id}: {error}")
logger.exception("Unhandled exception")  # Includes full traceback
```

Never use `print()` for logging in production code.

## Imports

Use absolute imports only, ordered as stdlib → third-party → local:

```python
# stdlib
import asyncio
from pathlib import Path

# third-party
from pydantic import BaseModel
from pydantic_ai import Agent

# local
from app.config.config_app import PROJECT_NAME
from app.data_models.app_models import ChatConfig
from app.utils.log import logger
```

Never use relative imports (`from .models import X`).

## Async Patterns

### Async Function Definition

```python
from pydantic_ai import Agent
from app.utils.log import logger

async def run_agent(agent: Agent, query: str) -> dict:
    """Run agent with async/await pattern."""
    try:
        result = await agent.run(user_prompt=query)
        return result
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise
```

### Timeout Handling

```python
import asyncio

async def evaluate_with_timeout(data: dict, timeout: float = 30.0) -> dict | None:
    """Execute evaluation with timeout protection."""
    try:
        async with asyncio.timeout(timeout):
            return await _run_evaluation(data)
    except TimeoutError:
        logger.error(f"Evaluation timed out after {timeout}s")
        return None
```

### Concurrent Execution

```python
async def process_multiple_items(items: list[str]) -> list[dict]:
    """Process items concurrently, filter exceptions."""
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

## Testing

For comprehensive testing guidance, see:

- **[testing-strategy.md](testing-strategy.md)** - What to test,
  TDD/BDD approach, mocking strategy, test organization
- **[tdd-best-practices.md](tdd-best-practices.md)** - Red-Green-Refactor
  cycle, AAA structure, test patterns
- **[bdd-best-practices.md](bdd-best-practices.md)** - Given-When-Then
  scenarios for stakeholder collaboration

For all make recipes and validation commands, see the project's CONTRIBUTING.md.

## Common Mistakes

| Mistake | Impact | Fix |
| ------- | ------ | --- |
| Hardcoded API keys | Security breach | Use `BaseSettings` with `.env` |
| `Optional[str]` syntax | Outdated style | Use `str \| None` |
| `List[str]` annotation | Outdated style | Use `list[str]` |
| Relative imports | Import errors | Use absolute `from app.x import Y` |
| Bare `except:` | Hidden errors | Catch specific exceptions |
| Missing type hints | Type errors | Add annotations to all functions |
| Direct dict access | Runtime errors | Use Pydantic models with validation |
| `print()` for logging | No production logs | Use `logger.info/error()` |
| Generic error messages | Hard to debug | Use error factory functions |
| Missing `from e` chain | Lost stack trace | Always chain: `raise ... from e` |
| No input validation | Security risks | Use Pydantic `Field()` constraints |
| String SQL queries | SQL injection | Use parameterized queries |
| Unsafe deserialization | Code execution | Use JSON/YAML with SafeLoader |

## Performance Patterns

### Bottleneck Detection

```python
def detect_bottlenecks(tier_times: dict[str, float], total_time: float) -> None:
    """Log performance bottlenecks exceeding 40% of total time."""
    threshold = total_time * 0.4
    for tier, time_taken in tier_times.items():
        if time_taken > threshold:
            logger.warning(
                f"Bottleneck: {tier} took {time_taken:.2f}s "
                f"({time_taken/total_time*100:.1f}% of total)"
            )
```

### Concurrent I/O

```python
# Concurrent API calls
async def fetch_multiple_papers(paper_ids: list[str]) -> list[dict]:
    """Fetch papers concurrently."""
    tasks = [fetch_paper(paper_id) for paper_id in paper_ids]
    return await asyncio.gather(*tasks)
```

## Pre-Commit Checklist

### Security

- [ ] No hardcoded secrets or API keys
- [ ] Credentials loaded via `BaseSettings` from `.env`
- [ ] External input validated with Pydantic models
- [ ] SQL queries use parameterized statements
- [ ] YAML loaded with `SafeLoader`
- [ ] No unsafe deserialization of untrusted data

### Type Safety

- [ ] All functions have type annotations
- [ ] Modern syntax used (`str | None`, `list[str]`)
- [ ] Pydantic models used for data validation at boundaries
- [ ] `Field()` constraints defined where needed

### Code Quality

- [ ] Absolute imports only (`from app.x import Y`)
- [ ] Import order: stdlib → third-party → local
- [ ] Docstrings on all public functions/classes
- [ ] Error factory functions used for messages
- [ ] Specific exceptions caught (not bare `except:`)
- [ ] Exceptions chained with `raise ... from e`
- [ ] Loguru `logger` used (not `print()`)

### Testing & Validation

- [ ] Unit tests created for new functionality
- [ ] External dependencies mocked with `@patch`
- [ ] Async tests use `@pytest.mark.asyncio`
- [ ] `make validate` passes (ruff + pyright + pytest)

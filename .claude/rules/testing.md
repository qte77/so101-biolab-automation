---
paths:
  - "tests/**/*.py"
---

# Testing Rules

- Mock external dependencies (HTTP, file systems, APIs)
- Use pytest with arrange/act/assert structure
- Mirror src/ structure in tests/
- Use tmp_path for filesystem isolation

# Lint & Type Tightening Checklist

Tighten one level at a time. Fix violations before tightening further.

## Lint Rules

| Language | Tool | Baseline | Recommended | Strict |
|----------|------|----------|-------------|--------|
| Python | ruff | E, F, I | +B, S, SIM, RUF | +C90, ANN, PT |
| Rust | clippy | default | `clippy::pedantic` | `clippy::restriction` (selective) |
| C/C++ | clang-tidy | core | +`bugprone-*`, `cppcoreguidelines-*`, `modernize-*` | +`cert-*`, `hicpp-*` |
| C/C++ | cppcheck | default | `--enable=warning,style` | `--enable=all` |
| C# | dotnet analyzers | default | `CA*` (all categories) | `TreatWarningsAsErrors` |
| C# | StyleCop | — | `SA*` rules | — |
| Go | golangci-lint | default | +errcheck, govet, staticcheck | +exhaustive, gocritic |
| TypeScript | eslint | recommended | +strict | +strict-type-checked |

## Type Checking

| Language | Tool | Baseline | Recommended | Strict |
|----------|------|----------|-------------|--------|
| Python | pyright | basic | standard | strict |
| Rust | rustc | default (already strict) | `#![deny(warnings)]` | `#![forbid(unsafe_code)]` |
| C/C++ | compiler flags | `-Wall` | `-Wall -Wextra` | `-Wall -Wextra -Werror -pedantic` |
| C# | `<Nullable>` | disable | enable | enable + `TreatWarningsAsErrors` |
| Go | go vet | default | +staticcheck | +nilaway |
| TypeScript | tsconfig | default | `strict: true` | +`noUncheckedIndexedAccess` |

## Formatting

| Language | Tool | Notes |
|----------|------|-------|
| Python | ruff format | `--check` for gate, no flag for fix |
| Rust | rustfmt | `--check` for gate |
| C/C++ | clang-format | `--dry-run -Werror` for gate |
| C# | dotnet format | `--verify-no-changes` for gate |
| Go | gofmt | `-l` for gate (lists unformatted) |
| TypeScript | prettier | `--check` for gate |

## Test Frameworks

| Language | Runner | Coverage | Property-based |
|----------|--------|----------|----------------|
| Python | pytest | coverage.py | Hypothesis |
| Rust | cargo test | cargo-tarpaulin | proptest |
| C/C++ | CTest / GoogleTest | gcov / lcov | — |
| C# | xUnit / NUnit | coverlet | FsCheck |
| Go | go test | go tool cover | rapid |
| TypeScript | vitest / jest | v8 / istanbul | fast-check |

## Per-file Ignores (common, justified)

| Rule | Where | Why |
|------|-------|-----|
| `assert` (S101) | test files | pytest requires assert |
| `subprocess` (S603) | trusted internal scripts | not user input |
| line length | generated files, test data | readability tradeoff |

## Cognitive Complexity

| Language | Tool | Gate threshold | Notes |
|----------|------|---------------|-------|
| Python | complexipy | 15/function | `complexipy app/ --max-complexity-allowed 15` |
| Rust | clippy `cognitive_complexity` | 25 (default) | built into clippy |
| C/C++ | clang-tidy `readability-function-cognitive-complexity` | 25 | configurable |
| TypeScript | eslint `complexity` | 20 | cyclomatic, not cognitive |

## Snapshot Testing

| Language | Tool | Purpose |
|----------|------|---------|
| Python | inline-snapshot | Regression contracts for API shapes, config defaults |
| Rust | insta | Snapshot testing for serialized output |
| TypeScript | vitest inline snapshots | `expect(x).toMatchInlineSnapshot()` |

## Gate vs Fix Split

Every project needs two recipes:

```
autofix    — format + lint --fix (developer convenience)
lint       — format --check + lint (CI gate, fails on issues)
complexity — cognitive complexity check (gate, fails above threshold)
validate   — lint + types + tests + coverage (full gate, must pass before commit)
```

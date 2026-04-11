# Context Management (ACE-FCA)

Principles for optimal context window utilization.

## Context Quality Equation

Quality output = Correct context + Complete context + Minimal noise

## Degradation Hierarchy (worst to best)

1. **Incorrect information** - worst, causes cascading errors (garbage in, garbage out)
2. **Missing information** - leads to assumptions (agent guesses, sometimes wrong)
3. **Excessive noise** - dilutes signal, wastes capacity (truth buried but still there)

Better to have less correct info than more info with errors.

## Utilization Target

Keep context at **40-60%** capacity. Leave room for:

- Model reasoning
- Output generation
- Error recovery

## Context Pollution Sources (What)

These mess up context - compact/summarize immediately:

- File searches (glob/grep results)
- Code flow traces
- Edit applications
- Test/build logs
- Large JSON blobs from tools

## Workflow Phases

Research → Planning → Implementation. Compact after each phase transition.

## Compaction Triggers (When)

Use `compacting-context` skill when:

- Verbose tool output (logs, JSON, search results)
- After completing a phase or milestone
- Before starting new complex task

## Subagent Usage

Use `researching-codebase` skill to:

- Isolate discovery artifacts from main context
- Return structured findings only
- Prevent search noise pollution

## Output Guidelines

- Prefer structured summaries over raw dumps
- Extract only relevant portions from large files
- Use targeted searches, not broad sweeps

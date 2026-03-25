# Context Management

## Quality Equation

Quality output = Correct context + Complete context + Minimal noise

Incorrect info > Missing info > Excessive noise (worst to best).

## Utilization Target

Keep context at **40-60%** capacity. Leave room for reasoning, output, and
error recovery.

## Pollution Sources

Compact or summarize immediately after:

- File searches (glob/grep results)
- Code flow traces and edit applications
- Test/build logs
- Large JSON blobs from tools

## Workflow Phases

Research → Planning → Implementation. Compact after each phase transition.

## Subagent Usage

Use research subagents to:

- Isolate discovery artifacts from main context
- Return structured findings only
- Prevent search noise pollution

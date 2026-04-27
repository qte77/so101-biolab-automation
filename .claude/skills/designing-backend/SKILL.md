---
name: designing-backend
description: Designs concise, streamlined backend systems matching exact task requirements. Use when planning APIs, data models, system architecture, or when the user requests backend design work.
compatibility: Designed for Claude Code
metadata:
  allowed-tools: Read, Grep, Glob, WebSearch, WebFetch
  argument-hint: [component-name]
  context: fork
  agent: Explore
  stability: stable
  content-hash: sha256:a0726df430d19c4dc24580413b05a81905470ed5af7006efaef7f96e226b1c59
  last-verified-cc-version: 1.0.34
---

# Skill

## Git Context

- Recent changes: !`git log --oneline -3`
- Current branch: !`git branch --show-current`

## Backend Architecture

**Target**: $ARGUMENTS

Creates **focused, streamlined** backend system designs matching stated
requirements exactly. No over-engineering.

## Workflow

1. **Read backend requirements** from specified documents
2. **Validate scope** - Simple data processing vs Complex system architecture
3. **Design minimal solution** matching stated complexity
4. **Create focused deliverables** - single doc for simple, multiple for complex
5. **Use make recipes** for all commands

## Architecture Strategy

**Simple Processing**: Basic functions, lightweight integration, existing patterns
**Complex Systems**: Multi-tiered pipelines, PydanticAI orchestration, async patterns
**Performance targets**: <1s simple operations, scalable for complex systems

## Output Standards

**Simple Tasks**: Single focused backend specification
**Complex Tasks**: Multiple targeted architecture files
**All outputs**: Concise, streamlined, no unnecessary complexity

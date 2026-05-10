# Tracker Constitution

## Core Principles

### I. Habit-First Design
Every feature maps to Atomic Habits concepts (4 laws: Cue → Craving → Response → Reward, identity-based habits, habit stacking, streak tracking, 1% improvements). The domain drives the design — no generic CRUD. Features exist to serve the method.

### II. Local & Offline-First
All data stored locally. Works without internet. Sync/collaboration is a future layer, never a requirement for v1. Privacy, speed, and zero-config simplicity.

### III. CLI + Optional Web UI
Core interactions via terminal (CLI). Web dashboard for visualization only — never for data entry. Ship the CLI fast; visuals are a secondary concern.

### IV. Test-Driven (NON-NEGOTIABLE)
Tests written before code. Red → Green → Refactor cycle strictly enforced. pytest with minimum 80% coverage on all modules.

### V. Simplicity (YAGNI)
Start with the smallest useful version. No auth, no multi-user, no cloud, no accounts. Add features only when proven necessary by real usage patterns.

## Technical Constraints

- **Language:** Python 3.11+
- **Storage:** SQLite (single file, zero setup, portable)
- **Package manager:** uv
- **Linting:** ruff + mypy (strict mode)
- **Testing:** pytest with coverage
- **CLI framework:** argparse or click (TBD in plan phase)

## Governance

- Constitution supersedes all other practices and preferences
- Any deviation must be documented and justified
- Amendments require: documentation, rationale, and migration plan
- All PRs/commits must verify compliance with core principles

**Version**: 1.0.0 | **Ratified**: 2025-05-10 | **Last Amended**: 2025-05-10

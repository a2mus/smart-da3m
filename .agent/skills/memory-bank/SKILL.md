---
name: memory-bank
version: 1
description: >
  Persistent cross-session memory protocol. Load this skill whenever the user
  asks to initialize, read, update, or review the project Memory Bank, or
  whenever context about architecture, progress, or current state is needed.
agents: [main_agent, general_purpose]
---

# Memory Bank Protocol — The Brain

## What is the Memory Bank?

The Memory Bank is a structured set of Markdown files stored in `memory-bank/`
at the project root. It is the **single source of truth** for all cross-session
context. Because Antigravity agents start each session without memory of previous
ones, every session MUST begin by reading the Memory Bank files in order.

---

## Boot Sequence (Start of Every Session)

Read these files **in order** before any other action:

1. `memory-bank/core/current-state.md` — 🎯 **THE NOW** — Active tasks, current phase, blockers.
2. `memory-bank/core/projectBrief.md` — 📋 **THE MISSION** — What we are building and why.
3. `memory-bank/core/productContext.md` — 👥 **THE USER** — Target audience, UX goals, constraints.
4. `memory-bank/core/techContext.md` — 🔧 **THE STACK** — Languages, versions, dependencies, config.
5. `memory-bank/core/patterns.md` — 🏗️ **THE PATTERNS** — Architecture decisions and code conventions.
6. `memory-bank/core/progress.md` — 📊 **THE HISTORY** — Completed milestones, known issues.
7. `memory-bank/core/next-session.md` — 📝 **THE HANDOVER** — Notes left by the previous session.

If any file is missing, create it with a minimal template and inform the user.

---

## Closing Protocol (End of Every Session)

Before ending a session, always update:

1. **`current-state.md`** — Reflect what changed this session (tasks done, new blockers).
2. **`progress.md`** — Append completed milestones with date (use `YYYY-MM-DD` format — always check system date first).
3. **`next-session.md`** — Write clear, specific instructions for the next agent session:
   - What was last touched
   - What to do first
   - Any open decisions the user must make

---

## File Templates

### `current-state.md`
```markdown
# Current State

**Phase:** [e.g., "MVP Development – Sprint 2"]
**Last updated:** YYYY-MM-DD

## Active Tasks
- [ ] Task description

## Blockers
- None

## Context Notes
(Anything the next agent needs to know immediately)
```

### `projectBrief.md`
```markdown
# Project Brief

## What We Are Building
(One paragraph max — clear, specific)

## Goals
- Goal 1
- Goal 2

## Non-Goals
- What we are explicitly NOT doing

## Success Criteria
- Measurable outcomes
```

### `productContext.md`
```markdown
# Product Context

## Target Users
(Who uses this, their level, their needs)

## Key User Flows
1. Flow description

## UX Constraints
- (e.g., mobile-first, offline support, RTL for Arabic)
```

### `techContext.md`
```markdown
# Technical Context

## Stack
| Layer       | Technology        | Version |
|-------------|-------------------|---------|
| Language    |                   |         |
| Framework   |                   |         |
| Database    |                   |         |
| Deploy      |                   |         |

## Key Dependencies
(Libraries that define architecture choices)

## Environment
- Dev: (setup instructions)
- Prod: (deployment target)

## Configuration
(Env vars, secrets structure — no actual values)
```

### `patterns.md`
```markdown
# Architecture & Code Patterns

## Architecture Decisions
- **ADR-001:** [Decision] — [Rationale]

## Code Conventions
- Naming: 
- File structure:
- Error handling:
- Testing approach:

## Patterns to Enforce
(Patterns the agent must always follow)

## Anti-Patterns to Avoid
(What we explicitly decided not to do)
```

### `progress.md`
```markdown
# Progress Log

## Milestones Completed
| Date       | Milestone                     | Notes |
|------------|-------------------------------|-------|
| YYYY-MM-DD | Initial scaffolding           |       |

## Known Issues
- Issue description (priority: high/medium/low)

## Deferred Items
- Items moved to backlog
```

### `next-session.md`
```markdown
# Next Session Handover

**Written by:** Agent on YYYY-MM-DD

## Start Here
(First thing to do next session)

## Open Decisions
- Decision needed from user: ...

## Files Last Modified
- `path/to/file.ext` — what changed

## Warnings
(Anything tricky or incomplete)
```

---

## Operational Rules

1. **Date verification first** — Before writing any date to a Memory Bank file, check the system date. Never assume or hallucinate dates.

2. **Read before write** — Never update a Memory Bank file without first reading its current content. Preserve existing entries.

3. **Append, don't overwrite progress** — `progress.md` entries are append-only. Old entries must never be deleted.

4. **Keep files lean** — If any file exceeds ~150 lines, split content into linked sub-files and update the index.

5. **Self-maintenance (The Gardener)** — When a new architectural pattern or decision is made during a session:
   - Add it to `patterns.md` immediately.
   - If a pattern is project-specific and reusable, suggest creating a new dedicated Skill.

6. **Memory Bank is sacred** — Never delete or significantly restructure the `memory-bank/` folder without explicit user confirmation. All edits are reversible via Git.

---

## Initialization Command

When the user says **"initialize memory bank"** or **"create memory bank"**:

1. Create `memory-bank/core/` directory.
2. Generate all 7 files above with their templates.
3. Prompt the user to fill in `projectBrief.md` and `techContext.md` first.
4. Confirm: "Memory Bank initialized. Please review `memory-bank/core/projectBrief.md` and fill in your project details."

---

## Memory Bank Location

```
project-root/
└── memory-bank/
    └── core/
        ├── current-state.md   ← Read FIRST every session
        ├── projectBrief.md
        ├── productContext.md
        ├── techContext.md
        ├── patterns.md
        ├── progress.md
        └── next-session.md    ← Read LAST before starting work
```


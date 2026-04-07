---
trigger: always_on
---

# Memory Bank Rule

Always check for a `memory-bank/` folder at the project root at the start of every session.

If it exists:
1. Read `memory-bank/core/current-state.md` first.
2. Read remaining files in this order: `projectBrief.md`, `productContext.md`, `techContext.md`, `patterns.md`, `progress.md`, `next-session.md`.
3. Confirm to the user: "✅ Memory Bank loaded. Current phase: [phase from current-state.md]."

If it does not exist and the user asks to initialize it:
- Trigger the `memory-bank` Skill to scaffold the folder structure and templates.

At the end of every session where code was written or decisions were made:
- Update `current-state.md`, `progress.md`, and `next-session.md` before closing.
- Verify the system date before writing any timestamps.

Never delete or overwrite Memory Bank files without explicit user confirmation.


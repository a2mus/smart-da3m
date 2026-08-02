---
name: bmad-loop-check-stuck
description: Comprehensive diagnostic workflow and automated checker to detect if bmad-loop is stuck, frozen, or failing, pinpoint the exact root cause, and provide actionable self-healing recovery steps.
---

# bmad-loop Health Check & Diagnostics Skill

Use this skill whenever the user asks to check if `bmad-loop` is stuck, hanging, frozen, or failing, or requests diagnostics and fixes for an active `bmad-loop` run.

## 🛠️ Automated Diagnostic Script

Run the automated diagnostic script to inspect engine processes, log errors, and heartbeat files:

```bash
python .agents/skills/bmad-loop-check-stuck/scripts/check_stuck.py
```

---

## 🔍 Diagnostic Checklist & Root Cause Analysis

When evaluating whether `bmad-loop` is stuck or hanging, inspect these 4 core dimensions:

### 1. Engine Process & Run State
- **PID File:** Read `.bmad-loop/runs/<run_id>/engine.pid`.
- **Process Check:** Verify if the PID process (`python`) is running in Task Manager / OS process list.
- **State Check:** Inspect `.bmad-loop/runs/<run_id>/state.json` to identify active story keys and current phase (`dev-running`, `review-running`, etc.).
- **Action:** If the engine process is dead or terminated:
  ```powershell
  python -m bmad_loop resume
  ```

### 2. OpenCode Subagent Model Errors (Server Logs)
- **Location:** `.bmad-loop/runs/<run_id>/logs/*.server.out`
- **Known Failure Patterns:**
  - `ProviderModelNotFoundError: Model not found: ...`
  - `AI_APICallError: Forbidden`
- **Root Cause:** Subagents (e.g. `oh-my-opencode` / `sisyphus-junior` / `Blind Hunter` / `Edge Case Hunter`) defaulted to unconfigured or unauthorized model endpoints (`claude-opus-4-7`, `gpt-5.5`, `glm-5`).
- **Fix:** Update `C:\Users\localadmin\.config\opencode\oh-my-opencode.json` to map all agent roles and categories to working models (`antigravity-manager/gemini-3.6-flash-high` or `nvidia/...` NIM models).

### 3. Stale Task Heartbeats
- **Location:** `.bmad-loop/runs/<run_id>/tasks/<task_id>/heartbeat.json`
- **Verification:** Check `ts` timestamp against current time.
- **Interpretation:** If `ts` has not updated in > 5–10 minutes while the PID is running, a subagent call is hanging synchronously waiting for a response that will never arrive.
- **Fix:** Stop the hung process and resume:
  ```powershell
  python -m bmad_loop stop
  python -m bmad_loop resume
  ```

### 4. Git Merge Conflict Markers & Pre-Commit Failures
- **Location:** Project source code files (`*.vue`, `*.ts`, `*.py`)
- **Symptoms:** Pre-commit hooks (`husky`, `eslint`, `stylelint`) fail with `Parsing error: Merge conflict marker encountered`.
- **Fix:** Search for `<<<<<<<` across workspace files, clean up conflict markers, and verify linting passes (`npm --prefix frontend run lint`).

---

## 📋 Standard Self-Healing Recovery Workflow

1. Execute diagnostic check:
   ```powershell
   python .agents/skills/bmad-loop-check-stuck/scripts/check_stuck.py
   ```
2. Verify subagent model mappings in `C:\Users\localadmin\.config\opencode\oh-my-opencode.json`.
3. Clean up any leftover git conflict markers in modified files.
4. Soft-stop the hung loop:
   ```powershell
   python -m bmad_loop stop
   ```
5. Resume loop execution:
   ```powershell
   python -m bmad_loop resume
   ```

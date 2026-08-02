#!/usr/bin/env python3
"""
bmad-loop Diagnostic & Health Checker
Comprehensive tool to inspect active bmad-loop runs, engine process health, task heartbeats, server logs, and git status.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

# Enforce UTF-8 stdout formatting if supported
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def find_latest_run(project_root: Path) -> Path | None:
    runs_dir = project_root / ".bmad-loop" / "runs"
    if not runs_dir.exists():
        return None
    run_folders = [f for f in runs_dir.iterdir() if f.is_dir()]
    if not run_folders:
        return None
    run_folders.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return run_folders[0]


def check_engine_pid(run_dir: Path) -> dict:
    pid_file = run_dir / "engine.pid"
    if not pid_file.exists():
        return {"running": False, "pid": None, "reason": "No engine.pid file found"}
    try:
        content = pid_file.read_text(encoding="utf-8").strip().split()
        pid = int(content[0])
    except Exception as e:
        return {"running": False, "pid": None, "reason": f"Failed to parse engine.pid: {e}"}

    running = False
    if sys.platform == "win32":
        import subprocess

        res = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True,
            text=True,
        )
        running = str(pid) in res.stdout
    else:
        try:
            os.kill(pid, 0)
            running = True
        except OSError:
            running = False

    return {"running": running, "pid": pid}


def check_logs(run_dir: Path) -> list:
    issues = []
    logs_dir = run_dir / "logs"
    if not logs_dir.exists():
        return issues

    for log_file in logs_dir.glob("*.server.out"):
        try:
            text = log_file.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            for idx, line in enumerate(lines[-300:]):
                if "ProviderModelNotFoundError" in line:
                    match = re.search(r"Model not found:\s*([^\.\?\"]+)", line)
                    model_str = match.group(1) if match else "unknown"
                    issues.append({
                        "type": "MODEL_NOT_FOUND",
                        "log_file": log_file.name,
                        "line": line,
                        "model": model_str,
                        "fix": f"Model '{model_str}' is missing or invalid. Update C:\\Users\\localadmin\\.config\\opencode\\oh-my-opencode.json to route roles to an active model (e.g. antigravity-manager/gemini-3.6-flash-high or nvidia/deepseek-ai/deepseek-v4-pro).",
                    })
                elif "AI_APICallError: Forbidden" in line:
                    issues.append({
                        "type": "API_FORBIDDEN",
                        "log_file": log_file.name,
                        "line": line,
                        "fix": "Third-party API key forbidden or unauthorized. Ensure subagents route through working antigravity-manager or nvidia NIM endpoints.",
                    })
                elif "Merge conflict marker encountered" in line or "<<<<<<<" in line:
                    issues.append({
                        "type": "GIT_CONFLICT_MARKER",
                        "log_file": log_file.name,
                        "line": line,
                        "fix": "Unresolved git merge conflict markers in source files. Clean up markers before committing.",
                    })
        except Exception:
            pass

    return issues


def check_heartbeats(run_dir: Path) -> list:
    stale_tasks = []
    now = time.time()
    tasks_dir = run_dir / "tasks"
    if not tasks_dir.exists():
        return stale_tasks

    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir():
            continue
        hb = task_dir / "heartbeat.json"
        if hb.exists():
            try:
                data = json.loads(hb.read_text(encoding="utf-8"))
                ts = data.get("ts", 0)
                elapsed = now - ts
                if elapsed > 300:  # > 5 minutes without update
                    stale_tasks.append({
                        "task_id": task_dir.name,
                        "last_heartbeat_ago_sec": int(elapsed),
                        "stall_armed": data.get("stall_armed", False),
                    })
            except Exception:
                pass
    return stale_tasks


def main():
    project_root = Path.cwd()
    run_dir = find_latest_run(project_root)

    if not run_dir:
        print("[ERROR] No active or past bmad-loop runs found in .bmad-loop/runs/")
        sys.exit(1)

    print(f"[INSPECT] Analyzing latest bmad-loop run: {run_dir.name}")

    state_file = run_dir / "state.json"
    active_story = "Unknown"
    phase = "Unknown"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            for key, task in state.get("tasks", {}).items():
                if task.get("phase") not in ["done", "deferred"]:
                    active_story = key
                    phase = task.get("phase", "Unknown")
        except Exception:
            pass

    print(f"  - Active Story: {active_story}")
    print(f"  - Current Phase: {phase}")

    pid_info = check_engine_pid(run_dir)
    status_str = "RUNNING" if pid_info.get("running") else "NOT RUNNING"
    print(f"  - Engine Process (PID {pid_info.get('pid')}): {status_str}")

    log_issues = check_logs(run_dir)
    stale_tasks = check_heartbeats(run_dir)

    print("\n--- DIAGNOSTIC FINDINGS ---")
    stuck = False

    if not pid_info.get("running"):
        stuck = True
        print("[ISSUE] Engine process is not running. The loop crashed, finished, or was terminated.")
        print("  -> FIX: Run `python -m bmad_loop resume` to continue.")

    if log_issues:
        stuck = True
        print(f"[ISSUE] Found {len(log_issues)} errors in OpenCode server logs:")
        for issue in log_issues[:5]:
            print(f"  - [{issue['type']}] in {issue['log_file']}: {issue['fix']}")

    if stale_tasks:
        stuck = True
        print(f"[ISSUE] Found {len(stale_tasks)} stale tasks (no heartbeat update for >5 min):")
        for task in stale_tasks[:5]:
            print(f"  - Task {task['task_id']} inactive for {task['last_heartbeat_ago_sec']}s")

    if not stuck:
        print("[STATUS] bmad-loop appears HEALTHY and actively processing.")
    else:
        print("\n[VERDICT] bmad-loop appears STUCK or ERRORED.")
        print("\n--- RECOMMENDED RECOVERY STEPS ---")
        print("1. Apply log/model fixes indicated above (check C:\\Users\\localadmin\\.config\\opencode\\oh-my-opencode.json).")
        print("2. Stop the hung process: python -m bmad_loop stop")
        print("3. Resume execution: python -m bmad_loop resume")


if __name__ == "__main__":
    main()

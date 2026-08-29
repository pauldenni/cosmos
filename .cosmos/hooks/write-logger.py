#!/usr/bin/env python3
"""
PostToolUse hook — logs every Write/Edit to .cosmos/run-log.md.
Fires automatically after Claude writes a file; never blocks the main flow.
"""
import json
import os
import sys
from datetime import datetime

SKIP = (
    ".cosmos/hooks/",
    ".cosmos/run-log.md",
    ".claude/",
    "memory/",
    "MEMORY.md",
)

def infer_command(path):
    if "journal/briefs/" in path:
        return "/brief"
    if "journal/scans/" in path:
        return "/scan"
    if "journal/meetings/" in path or "journal/personal/" in path:
        return "/prep"
    return "/sync"

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = payload.get("tool_name", "")
    if tool not in ("Write", "Edit"):
        sys.exit(0)

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Derive the vault root from this script's own location (.cosmos/hooks/ -> root),
    # not from cwd. cwd is whatever the shell happened to be in, and is not the vault
    # at all under a scheduled task.
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rel = file_path[len(root):].lstrip("/") if file_path.startswith(root) else file_path

    if any(s in rel for s in SKIP):
        sys.exit(0)

    command = infer_command(rel)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} | {tool.lower():5} | {command} | {rel}\n"

    log = os.path.join(root, ".cosmos", "run-log.md")
    with open(log, "a") as f:
        f.write(line)

if __name__ == "__main__":
    main()

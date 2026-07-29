#!/usr/bin/env python3
# PreToolUse guard — deterministic enforcement layer of Rule 02 (Destructive Action Barrier).
# Reads the tool-call JSON from stdin; exit code 2 blocks the call and feeds stderr back to the model.
import json
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # not parseable -> do not block

cmd = (data.get("tool_input") or {}).get("command", "") or ""


def block(reason):
    print(
        f"BLOCKED by Destructive Action Barrier (Rule 02): {reason}. "
        f"This operation requires explicit human approval — ask the operator instead.",
        file=sys.stderr,
    )
    sys.exit(2)


# rm with both recursive and force flags (any order, combined or separate, incl. long
# forms, absolute paths like /bin/rm, and rm reached via xargs)
for segment in re.split(r"[|;&]", cmd):
    tokens = segment.split()
    if any(t == "rm" or t.endswith("/rm") for t in tokens):
        flags = " ".join(t for t in tokens if t.startswith("-"))
        recursive = bool(re.search(r"-\w*[rR]|--recursive", flags))
        force = bool(re.search(r"-\w*f|--force", flags))
        if recursive and force:
            block("recursive force-delete (rm -rf)")

PATTERNS = [
    (r"\bmkfs(\.\w+)?\b", "filesystem format (mkfs)"),
    (r"\bdd\b[^|;&]*\bof=/dev/", "raw write to a block device (dd of=/dev/...)"),
    (r"\bgit\s+push\b[^|;&]*(\s--force\b|\s-f\b)", "force push (git push --force)"),
    (r"\bgit\s+push\b[^|;&]*\s\+\S+", "force push via refspec (git push origin +branch)"),
    (r"\bfind\b[^|;&]*\s-delete\b", "bulk delete (find ... -delete)"),
    (r"(?i)\bdrop\s+(database|table|tablespace|schema)\b", "SQL DROP statement"),
    (r"\bterraform\s+(destroy|apply\s+-destroy)\b", "terraform destroy"),
    (r"\bkubectl\s+delete\s+(namespace|ns)\b", "kubectl namespace deletion"),
    (r"\baws\s+\S+\s+(delete|terminate)-\S+", "AWS resource deletion"),
    (r"\bgcloud\b[^|;&]*\bdelete\b", "GCP resource deletion"),
]
for pattern, reason in PATTERNS:
    if re.search(pattern, cmd):
        block(reason)

sys.exit(0)

#!/usr/bin/env python3
# PreToolUse guard — deterministic enforcement layer of Rule 02 (Destructive Action Barrier).
# Reads the tool-call JSON from stdin; exit code 2 blocks the call and feeds stderr back to the model.
# It matches command text, so it is a tripwire against mistakes, not a security boundary (Rule 02 §5).
# It exits only 0 or 2, as the settings.json handler's onFailure: block expects.
import json
import re
import sys


def block(reason):
    print(
        f"BLOCKED by Destructive Action Barrier (Rule 02): {reason}. "
        f"This is blocked by policy and cannot be approved inside this session. Give the operator "
        f"the exact command to run themselves; do not retry it in another form.",
        file=sys.stderr,
    )
    sys.exit(2)


try:
    data = json.load(sys.stdin)
except Exception:
    block("unreadable hook input")

tool_input = data.get("tool_input") if isinstance(data, dict) else None
cmd = tool_input.get("command") if isinstance(tool_input, dict) else None
if cmd is None:
    cmd = ""
if not isinstance(cmd, str):
    block("unreadable hook input")
# Undo line continuations and the ${IFS} trick so the text splits the way the shell would.
cmd = re.sub(r"\$\{?IFS\}?", " ", cmd.replace("\\\n", " "))

# rm with both recursive and force flags (any order, combined or separate, incl. long forms,
# absolute paths like /bin/rm, quoted or escaped names, and rm inside sh -c, eval, xargs,
# subshells and command substitutions)
for segment in re.split(r"\$\(|[|;&()`\n]", cmd):
    raw = segment.split()
    tokens = [t.strip("\\\"'{}$") for t in raw]
    for i, t in enumerate(tokens):
        if t == "rm" or t.endswith("/rm"):
            first = raw[i]
            # A quote that opens a multi-word string is data (grep, echo, commit -m), unless it feeds sh -c or eval.
            if first[:1] in "\"'" and not first.endswith(first[0]) and i > 0 and tokens[i - 1] != "-c" and tokens[0] != "eval":
                continue
            flags = [f for f in tokens[i + 1:] if f.startswith("-")]
            recursive = any(re.fullmatch(r"-[A-Za-z]*[rR][A-Za-z]*|--recursive", f) for f in flags)
            force = any(re.fullmatch(r"-[A-Za-z]*f[A-Za-z]*|--force", f) for f in flags)
            if recursive and force:
                block("recursive force-delete (rm -rf)")

# Each pattern stays within one command segment and one line.
PATTERNS = [
    (r"\bmkfs(\.\w+)?\b", "filesystem format (mkfs)"),
    (r"\bdd\b[^|;&\n]*\bof=[\"']?/dev/", "raw write to a block device (dd of=/dev/...)"),
    (r"\bgit\b[^|;&\n]*\bpush\b[^|;&\n]*(\s--force\b|\s-[A-Za-z]*f[A-Za-z]*\b)", "force push (git push --force)"),
    (r"\bgit\b[^|;&\n]*\bpush\b[^|;&\n]*\s\+\S+", "force push via refspec (git push origin +branch)"),
    (r"\bfind\b[^|;&\n]*\s-delete\b", "bulk delete (find ... -delete)"),
    (r"(?i)\bdrop\s+(database|table|tablespace|schema)\b", "SQL DROP statement"),
    (r"\bterraform\b[^|;&\n]*\s(destroy(?=\s|$)|apply\b[^|;&\n]*\s-destroy\b)", "terraform destroy"),
    (r"\bkubectl\b[^|;&\n]*\bdelete\b[^|;&\n]*(?<![-=\w.])(?i:namespaces?|ns)(?=\s|/|$)", "kubectl namespace deletion"),
    (r"\baws\b[^|;&\n]*\s(delete|terminate)-[\w-]+", "AWS resource deletion"),
    (r"\baws\b[^|;&\n]*\ss3\s+(rm\b[^|;&\n]*--recursive|rb\b)", "AWS S3 bulk or bucket deletion"),
    (r"\bgcloud\b[^|;&\n]*\bdelete\b", "GCP resource deletion"),
    (r"(?i)\b(Remove-Item|ri|del|erase|rd|rmdir)\b[^|;&\n]*\s(-r\w*|/s)\b|\brm\b[^|;&\n]*\s-rec\w*\b", "recursive delete (Remove-Item -Recurse, rd /s)"),
    (r"(?i)\b(Format-Volume|Clear-Disk)\b", "PowerShell disk format"),
]
for pattern, reason in PATTERNS:
    if re.search(pattern, cmd):
        block(reason)

sys.exit(0)

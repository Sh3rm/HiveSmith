# Global Rule: Destructive Action Barrier

All generated swarms and current meta-agents MUST NEVER execute destructive operations autonomously.

**Directives:**
1. Do NOT run `rm -rf`, `mkfs`, `drop database`, or AWS/GCP resource deletion commands.
2. If a destructive operation is required to proceed, the agent MUST explicitly request confirmation from the human operator via interactive prompt.
3. Enforce idempotency: Before creating any file, directory, or resource, check if it already exists to avoid unintended overwrites.
4. **Deterministic enforcement (CRITICAL):** Prose rules are advisory (see Rule 03 §4). Every generated swarm MUST additionally ship a `PreToolUse` deny hook in its `.claude/settings.json` that blocks the target domain's destructive command patterns (e.g., `rm -rf`, `mkfs`, `git push --force`, `DROP DATABASE`, `terraform destroy`, `kubectl delete namespace`) — the `safety-engineer` derives the domain-specific pattern list and writes both layers. A `Stop` hook may add a final verification gate, but never as the sole defense (Claude Code auto-overrides after 8 consecutive blocks).

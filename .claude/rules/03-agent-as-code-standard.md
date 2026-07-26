# The "Agent as Code" Standard

Every single sub-agent and orchestrator generated in this workspace MUST strictly adhere to the following physical and structural standards. These are Claude Code's real, documented conventions — deviation produces a swarm that Claude Code silently fails to load. This applies to ALL generated swarms:

## 1. Physical Directory Structure
- **Orchestrator (`CLAUDE.md`):** MUST be written directly to the project root directory (e.g., `<project-root>/CLAUDE.md`). Plain markdown — Claude Code loads it automatically as project memory.
- **Sub-Agents:** MUST be written to `.claude/agents/<agent-name>.md` — one file per agent. Never write agent folders to the project root, and never use the legacy `.claude/skills/<name>/SKILL.md` layout for worker personas (skills are instruction packs, not isolated agents).
- **Global Rules:** MUST be written to `.claude/rules/<rule-name>.md`. Claude Code auto-loads every markdown file in this directory at startup. Optionally scope a rule to file patterns with `paths:` frontmatter.
- **Model & Project Settings:** MUST be written to `.claude/settings.json` (e.g., `{"model": "opus"}`).
- **Tooling (MCP):** Project-scoped MCP servers MUST be written to `<project-root>/.mcp.json` (NOT inside `.claude/`). Only add MCP servers for capabilities the native tools lack.

## 2. File Formats (CRITICAL)
- **`CLAUDE.md` MUST NOT contain YAML frontmatter.** It is plain markdown. Model configuration lives in `.claude/settings.json`.
- **Every `.claude/agents/<name>.md` MUST begin with a YAML frontmatter block.** Only `name` and `description` are required by Claude Code; everything else is optional:

```yaml
---
name: agent-name
description: Use this agent to <action-oriented trigger description — Claude Code uses this for automatic delegation>.
tools: Read, Grep, Glob
model: sonnet
---
```

- `name` (REQUIRED) SHOULD match the filename (without `.md`) — house convention for auditability; Claude Code itself identifies agents by `name`, not filename.
- `description` (REQUIRED) MUST be action-oriented ("Use this agent to/when ...") so the orchestrator can auto-delegate correctly.
- `tools` MUST be a least-privilege, comma-separated allowlist of real Claude Code tools: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebSearch`, `WebFetch` (plus MCP tool names when required). This list is enforced by Claude Code — it is the swarm's actual security boundary. Read-only analysts get `Read, Grep, Glob`; researchers get `WebSearch, WebFetch`; only file-producing workers get `Write`/`Edit`; only command-running workers get `Bash`. If omitted, the agent inherits ALL tools — omission is only acceptable with an explicit justification in the blueprint.
- `model` MUST be a Claude Code alias per the Model Routing Doctrine below, `inherit` (the default), or a full model ID when the blueprint pins one deliberately.
- **Advanced optional keys (all officially documented — use when the role justifies them, never reflexively):**
  - `disallowedTools:` — deny-list subtracted from the inherited/specified tools.
  - `effort:` — reasoning depth (`low`, `medium`, `high`, `xhigh`, `max`); overrides the session effort for this agent.
  - `isolation: worktree` — runs the agent in a temporary git worktree; assign it to agents that write files in parallel with other writers.
  - `permissionMode:` — `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan`; never generate `bypassPermissions` without explicit human approval.
  - `maxTurns:` — hard cap on agentic turns for runaway protection.
  - `skills:` — skill names preloaded (full content) into the agent's context at startup.
  - `mcpServers:` — per-agent MCP servers (named references or inline configs).
  - `hooks:` — lifecycle hooks scoped to this agent.
  - `memory:` — persistent memory scope (`user`, `project`, or `local`) for cross-session learning.
  - `color:` — display color in the task list (cosmetic).

> **FORBIDDEN FIELDS:** `max_output_tokens`, `enable_write_tools`, `enable_mcp_tools`, `enable_subagent_tools`, `planning-mode`. These are foreign (Antigravity) fields. Claude Code does not recognize them; emitting them is a schema violation that `qa-validator` MUST reject. Any key outside the documented set above is likewise a violation.

## 3. Direct File Writes
Do NOT output massive markdown templates inside JSON strings when communicating. If your job is to generate a file, write it directly to the disk using the `Write` tool or `Bash`.

## 4. Dynamic Model Routing (Future-Proof Optimization)
Do NOT hardcode specific model version strings in your architectural designs. Use tier-based aliases:
- **Heavy Reasoning / Orchestration (Frontier):** Assign `fable` for `domain-architect`, `persona-engineer`, etc.
- **Complex Coding (High Effort):** Assign `opus` as a strong alternative when `fable` is unavailable.
- **Data Synthesis (Medium Effort):** Assign `sonnet` for research synthesis or context integration.
- **Fast Parsing (Low Effort):** Assign `haiku` for rapid scanning (`qa-validator`, `repo-analyzer-worker`).
- **Match the caller:** Assign `inherit` when a worker should always run on whatever model the orchestrator is using.

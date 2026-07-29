# The "Agent as Code" Standard

Every single sub-agent and orchestrator generated in this workspace MUST strictly adhere to the following physical and structural standards. These are Claude Code's real, documented conventions — deviation produces a swarm that Claude Code silently fails to load. This applies to ALL generated swarms.

> **CANONICAL SOURCE:** This file is the single source of truth for the Claude Code file/frontmatter schema and the Model Routing Doctrine. Other files (CLAUDE.md, agent bodies) MUST reference this rule instead of restating its lists — duplicated copies drift out of sync and produce contradictions.

## 1. Physical Directory Structure
- **Orchestrator (`CLAUDE.md`):** MUST be written directly to the project root directory (e.g., `<project-root>/CLAUDE.md`). Plain markdown — Claude Code loads it automatically as project memory. It may import auxiliary files with the `@path/to/file` syntax (expanded at launch, up to 4 hops) to stay modular.
- **Sub-Agents:** MUST be written to `.claude/agents/<agent-name>.md` — one file per agent. Never write agent folders to the project root, and never use the `.claude/skills/<name>/SKILL.md` layout for worker personas (skills are instruction packs, not isolated agents).
- **Global Rules:** MUST be written to `.claude/rules/<rule-name>.md`. Claude Code auto-loads every markdown file in this directory at startup. Scope a rule to file patterns with `paths:` frontmatter (glob patterns, brace expansion supported) when it only applies to part of the tree — path-scoped rules load only when matching files are read, keeping sessions lean.
- **Skills (optional):** Reusable multi-step procedures or domain playbooks MAY be packaged under `.claude/skills/` and preloaded into a specific agent via its `skills:` frontmatter. Skills are for on-demand procedural knowledge; always-mandatory standards belong in `.claude/rules/` (auto-loaded), never in skills.
- **Model & Project Settings:** MUST be written to `.claude/settings.json`, carrying the swarm's default model tier from the blueprint (e.g., `{"model": "sonnet"}`) plus any guard hooks (see §4).
- **Tooling (MCP):** Project-scoped MCP servers MUST be written to `<project-root>/.mcp.json` (NOT inside `.claude/`). Only add MCP servers for capabilities the native tools lack. Prefer the explicit `enabledMcpjsonServers` allowlist over `enableAllProjectMcpServers: true` in settings — trust decisions must be visible.

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
- `description` (REQUIRED) MUST be action-oriented ("Use this agent to/when ...") so the orchestrator can auto-delegate correctly. For agents that should trigger without being named explicitly, include the officially recommended phrase "use PROACTIVELY" (e.g., "Use PROACTIVELY after code changes").
- `tools` MUST be a least-privilege, comma-separated allowlist of real Claude Code tools: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebSearch`, `WebFetch` (plus MCP tool names when required). This list is enforced by Claude Code — it is the swarm's actual security boundary. Read-only analysts get `Read, Grep, Glob`; researchers get `WebSearch, WebFetch`; only file-producing workers get `Write`/`Edit`; only command-running workers get `Bash`. If omitted, the agent inherits ALL tools — omission is only acceptable with an explicit justification in the blueprint.
- `model` MUST be a Claude Code alias per the Model Routing Doctrine below or `inherit` (the default). Full model version strings are forbidden by house doctrine (they break the future-proof alias routing — Rule 08 enforces the same restriction at blueprint level), even though Claude Code itself would accept them.
- **Advanced optional keys (all officially documented — use when the role justifies them, never reflexively):**
  - `disallowedTools:` — deny-list subtracted from the inherited/specified tools.
  - `effort:` — reasoning depth (`low`, `medium`, `high`, `xhigh`, `max`); overrides the session effort for this agent.
  - `isolation: worktree` — runs the agent in a temporary git worktree; assign it to agents that write files *inside the same git repository* in parallel with other writers. (Note: a worktree isolates the CURRENT repo only — it does not protect writes to paths outside the repo, which is why HiveSmith's own parallel Step-3 writers, who write distinct files into the target workspace, deliberately do not use it.)
  - `permissionMode:` — `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan` (`manual` is accepted as an alias of `default` on Claude Code ≥ 2.1.200); never generate `bypassPermissions` without explicit human approval.
  - `maxTurns:` — hard cap on agentic turns for runaway protection; assign it to loop-prone workers (open-ended researchers, repo scanners).
  - `skills:` — skill names preloaded (full content) into the agent's context at startup.
  - `mcpServers:` — per-agent MCP servers (named references or inline configs).
  - `hooks:` — lifecycle hooks scoped to this agent (see §4).
  - `memory:` — persistent memory scope (`user`, `project`, or `local`) for cross-session learning; assign it to agents whose judgment improves by accumulating lessons across runs.
  - `background: true` — always run this agent as a background task, even when the caller needs its result immediately.
  - `initialPrompt:` — auto-submitted first user turn when the agent runs as the main session agent (via `--agent` or the `agent` setting); irrelevant for orchestrator-invoked workers.
  - `color:` — display color in the task list (cosmetic).

> **FORBIDDEN FIELDS:** `max_output_tokens`, `enable_write_tools`, `enable_mcp_tools`, `enable_subagent_tools`, `planning-mode`. These are foreign (Antigravity) fields. Claude Code does not recognize them; emitting them is a schema violation that `qa-validator` MUST reject. Any key outside the documented set above is likewise a violation.

## 3. Context Inheritance & Anti-Duplication (CRITICAL)
Custom subagents automatically load the FULL memory hierarchy at startup — `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and every auto-loaded `.claude/rules/*.md` (official: sub-agents.md "What loads at startup"; only the built-in Explore and Plan agents skip it). Therefore:
- **NEVER copy global rules into individual agent bodies** — neither in HiveSmith's own roster nor in generated swarms. Duplicated text drifts out of sync over time and produces contradictions; the rules directory is the single source of truth that every agent already sees.
- Agent bodies contain ONLY role-specific content: responsibilities, constraints unique to the role, error handling, and output format. A one-line pointer ("per Rule 03", "per the Destructive Action Barrier") is acceptable where emphasis genuinely helps.
- What subagents do NOT inherit: the parent's conversation history and the parent's auto memory. Task-specific context (the Manifesto, file paths, prior decisions) must therefore still be passed explicitly in every delegation prompt.

## 4. Hooks: The Deterministic Enforcement Layer
`CLAUDE.md` and `.claude/rules/` are **advisory** — they are delivered as context, not enforced by the harness. Any constraint that must hold with ZERO exceptions (destructive-command bans, secret-file protection, mandatory format gates) MUST additionally be implemented as a hook, because hooks execute deterministically outside the model's discretion.
- **Where:** project-wide hooks in `.claude/settings.json`; role-scoped hooks in the agent's `hooks:` frontmatter.
- **Key events:** `PreToolUse` (gate/deny a tool call before it runs — exit code 2 or `"permissionDecision": "deny"` blocks it), `PostToolUse`, `Stop` (gate turn-end on a passing check — note: Claude Code auto-overrides after 8 consecutive blocks, so a Stop hook is a backstop, not the sole defense), `PreCompact`/`PostCompact`, `InstructionsLoaded`, `WorktreeCreate`/`WorktreeRemove`.
- **Hook types:** `command` (shell script — the default workhorse), `prompt` (single-turn LLM evaluation, Haiku by default), `agent` (multi-turn verification subagent with tool access — experimental), `http` (POST to an endpoint), `mcp_tool` (call a connected MCP tool).
- Generated swarms with a Destructive Action Barrier MUST ship a `PreToolUse` deny hook for the domain's destructive command patterns alongside the prose rule (see Rule 02).

## 5. Coordination: Subagents vs Agent Teams
Subagents CANNOT message each other mid-task — all coordination flows hub-and-spoke through the orchestrator. Design blueprints accordingly; never write prompts that assume peer-to-peer agent messaging exists. If a target domain genuinely requires direct inter-agent communication and shared task self-coordination, the sanctioned mechanism is **Agent Teams** (experimental; requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; teammates message each other directly and share a task list). Default recommendation remains the orchestrator-hub pattern — propose Agent Teams only with explicit justification in the blueprint, and mark the swarm as depending on an experimental feature.

Runtime behaviors to design around (Claude Code ≥ 2.1.198): subagents run in the **background by default** unless the caller needs the result immediately — the background tool reduction concerns interactive facilities (Artifact, plan-mode tools), NOT `WebSearch`/`WebFetch`/MCP tools, so backgrounded researchers keep their full research capability; and subagents **inherit the main session's extended-thinking setting** — there is no per-agent thinking override.

## 6. Direct File Writes
Do NOT output massive markdown templates inside JSON strings when communicating. If your job is to generate a file, write it directly to disk. Prefer the native `Write`/`Edit` tools over `Bash` heredocs/redirection for file content — native file tools are tracked by Claude Code's checkpointing, keeping every change reversible via `/rewind`; `Bash` is for directory creation (`mkdir -p`) and verification commands.

## 7. Dynamic Model Routing (Canonical Doctrine)
Do NOT hardcode specific model version strings in your architectural designs. Use tier-based aliases. This table is the ONE canonical tier mapping — `CLAUDE.md` and all agents defer to it:
- **`fable` — Frontier reasoning:** long-horizon autonomous work, orchestration-critical creation and architecture (the roles where a reasoning failure poisons everything downstream).
- **`opus` — Complex agentic coding & enterprise work:** Anthropic's official "start here" tier for complex implementation; the strong alternative when `fable` is unavailable or not warranted.
- **`sonnet` — Balanced default:** research, synthesis, integration — the best speed/intelligence combination for most production work.
- **`haiku` — Narrow, high-volume, fast tasks:** rapid scanning, classification, mechanical validation in generated swarms where the domain's cost profile matters.
- **`inherit` — Match the caller:** when a worker should always run on whatever model the orchestrator is using.

HiveSmith's OWN roster is deliberately generously tiered (see CLAUDE.md "Self-Routing") — it is a creator, and output quality outranks cost; the full four-tier doctrine including `haiku` applies to the swarms it GENERATES.

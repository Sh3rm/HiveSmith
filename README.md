# 🐝⚒️ HiveSmith

**You describe the swarm. HiveSmith forges it.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Powered by](https://img.shields.io/badge/Powered_by-Claude_Code-8b5cf6.svg)](https://code.claude.com/docs)
[![Verified against](https://img.shields.io/badge/Claude_Code-v2.1.288-22c55e.svg)](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
[![Agents](https://img.shields.io/badge/Sub--Agents-15-orange.svg)](#agent-roster)

A meta-agent system that designs and generates production-ready agent swarms, sized to the work: from a single well-tooled agent to an orchestrator with specialised workers. Built for the [Claude Code](https://code.claude.com/docs) CLI ecosystem.

You describe what you need. HiveSmith researches the domain, architects the agent hierarchy, writes every prompt and config file, validates the topology, and delivers a working swarm — ready to run with `claude`.

> **HiveSmith** — the smith that forges hives. Sister project of [SwarmForge](https://github.com/Sh3rm/SwarmForge) (the Gemini/Antigravity edition): same lineage, rebuilt from the ground up on Claude Code's native primitives: sub-agents, auto-loaded rules, and project MCP config. HiveSmith has since moved to a leaner pipeline with fewer agents.

## How It Works

HiveSmith is itself a swarm. An orchestrator (`CLAUDE.md`) coordinates 15 specialized sub-agents — each a real Claude Code sub-agent with its own isolated context window, tool allowlist, and model tier — through a clarifying step plus six working steps:

```
0. Clarify                   — Ask about missing constraints that change the design (skipped when the request is explicit)
1. Research                  — Launch only the researchers the request needs, in parallel; save their reports as files
2. Architecture              — Read the raw reports, resolve conflicts, design the blueprint (roster, tiers, state, hooks)
3. Infrastructure & Safety   — Safety rules + guard hooks; MCP config and custom tools only when the blueprint needs them
4. Persona Generation        — Write CLAUDE.md, .claude/agents/*.md, rules, and settings to disk
5. Verification              — Fresh-context evaluators audit prompts, schemas, dependencies and the DAG in parallel
6. Delivery                  — Hand the verified swarm tree to the user
```

If verification finds issues, the orchestrator routes them back to the architect or the persona engineer and re-verifies what changed. The user's request travels verbatim to every worker; research reports travel as file paths, never as compressed summaries.

## Key Design Decisions

- **Fewest Agents the Work Justifies.** Multi-agent systems typically spend 3-10x the tokens of a single agent on the same task, and splitting one body of work into sequential phases loses context at every handoff. So every agent in a generated swarm must stand on a stated ground — context isolation, genuinely parallel work, or a specialization threshold — and there is no target roster size; a single well-tooled agent with rules and hooks is a valid result. Generated instruction files keep only what the model cannot infer on its own, without stacked CRITICAL/MUST emphasis or role inflation (Rule 09).

- **Native Claude Code Sub-Agents.** Every worker persona is a `.claude/agents/<name>.md` file with the official frontmatter schema (`name`, `description`, `tools`, `model`, plus advanced keys — `effort`, `maxTurns`, `memory` — where the role justifies them). The orchestrator delegates through Claude Code's Agent tool, so each worker runs in an isolated context window with a least-privilege tool allowlist enforced by the harness itself — researchers can search but not write, validators can read but not modify.

- **Deterministic Guard Hooks.** The Destructive Action Barrier is not just prose: a `PreToolUse` hook (`.claude/hooks/block-destructive.py`) deterministically blocks `rm -rf`, `mkfs`, force-pushes, SQL `DROP`s, and cloud resource deletions before they run. Generated swarms ship the same dual layer — a rules file for context plus a domain-tailored guard hook for enforcement.

- **Tier-Based Model Routing with a Budget.** HiveSmith assigns models using Claude aliases (`fable`, `opus`, `sonnet`, `haiku`) based on cognitive load. Heavy reasoning and orchestration gets `fable` (Fable 5.1), complex coding gets `opus` (Opus 5.5), research gets `sonnet` (Sonnet 5.5), fast scanning gets `haiku` (Haiku 4.5). When Anthropic ships new models, the aliases resolve to the latest versions automatically. Generated swarms run on *your* subscription, so they follow a hard tier budget: an `opus` orchestrator, `sonnet` workers by default, `haiku` for mechanical roles, `opus` workers only with benchmark evidence, at most one `fable` agent, and never `effort: max` — the QA gate rejects rosters that break it. Effort is left at each model's official default unless the blueprint sets one (Opus 5.5 and Sonnet 5.5 default to `medium`, so verification and research roles in a generated swarm carry `effort: high`; a generated `settings.json` may carry `effortLevel: high` when the domain justifies it, and you can cap everything with `maxEffortLevel`). You can always edit the generated `settings.json` and agent frontmatter by hand afterwards. Operators can still re-route everything at launch with `CLAUDE_CODE_SUBAGENT_MODEL` (default for agents without a `model`) plus `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (makes it override every definition).

- **Research Before Architecture.** Every generated swarm can research its own domain, through dedicated researcher agents or, in a single-agent design, the orchestrator's own search tools. HiveSmith never relies on pre-trained knowledge for domain-specific decisions. It searches the web first, every time — via Claude Code's native `WebSearch`/`WebFetch` tools, with an optional tokenless [duckduckgo-mcp-server](https://pypi.org/project/duckduckgo-mcp-server/) fallback in `.mcp.json`.

- **Strict, Fresh-Context Verification.** The `qa-validator` checks the generated frontmatter schemas against Claude Code's real spec (and rejects foreign fields), enforces the tier budget, confirms every hook script and state file exists, runs dependency pre-flights (`uv`, `npx`), and validates directory structure; `prompt-evaluator` audits the prompts for measured anti-patterns and outdated prompting; `dag-validator` checks the delegation graph. None of them sees the authors' reasoning.

## Agent Roster

All 15 sub-agents live in `.claude/agents/`:

| Agent | Role | Default Tier |
|---|---|---|
| `domain-architect` | Reconciles the research and designs the blueprint: roster, tiers, shared state, hooks | Fable |
| `persona-engineer` | Writes all system prompts (CLAUDE.md, .claude/agents/*.md) | Fable |
| `prompt-evaluator` | Simulates edge cases and audits generated prompts for anti-patterns | Fable |
| `safety-engineer` | Generates domain-specific safety rules | Fable |
| `tool-smith` | Builds custom scripts when standard MCP tools aren't enough | Fable |
| `mcp-integrator` | Generates the project-root `.mcp.json` for the target swarm | Opus |
| `dag-validator` | Validates swarm topology — detects cycles, orphan agents, broken links | Opus |
| `researcher-google-cloud` | Google Cloud, Gemini best practices | Opus |
| `researcher-anthropic-openai` | Anthropic & OpenAI multi-agent patterns | Opus |
| `researcher-tech-stack` | Version verification, deprecation checks | Opus |
| `researcher-security` | OWASP, HITL, guardrail best practices | Opus |
| `researcher-academic-independent` | arXiv, independent AI research blogs | Opus |
| `researcher-vcs-github` | Mines GitHub/GitLab for existing agent configs | Opus |
| `repo-analyzer-worker` | Fast concurrent scanning of cloned repos | Sonnet |
| `qa-validator` | Schema validation, dependency checks, pass/fail reporting | Sonnet |

> "Default Tier" is set in each agent's `model:` frontmatter and applied automatically by Claude Code. HiveSmith's own roster is deliberately generously tiered — it is a creator, and the quality of what it forges is worth the tokens. The `haiku` tier remains part of the routing doctrine for the swarms HiveSmith generates.

## 🚀 Quick Start

HiveSmith is powered by [Claude Code](https://code.claude.com/docs).

**1. Prerequisites:**

- **[Claude Code CLI](https://code.claude.com/docs/en/quickstart)** — installed and authenticated (`claude` command available). Version **2.1.280 or newer** is required for the full doctrine (the `opus` alias resolving to Opus 5.5, the `omitClaudeMd` frontmatter key, `maxEffortLevel`, partial `maxTurns` results, `SubagentStop` hooks, the `experimental.cacheTtl` key, and the project-settings `defaultMode` behaviour the QA gate checks). The `sonnet` alias resolves to Sonnet 5.5 only on **2.1.284 or newer** and on the Anthropic API (older versions and other providers resolve an earlier Sonnet). HiveSmith was verified against v2.1.288.
- **[uv](https://docs.astral.sh/uv/)** — optional, only for the `uvx` DuckDuckGo MCP fallback

**2. Clone this repository:**

```bash
git clone https://github.com/Sh3rm/HiveSmith.git
cd HiveSmith
```

**3. Boot the swarm:**

```bash
claude "Build me a Kubernetes monitoring swarm with Prometheus and Grafana integration"
```

That's it. HiveSmith will research the domain, architect the agent hierarchy, write every prompt and config file, validate the output, and deliver a working swarm into your target directory.

> **Model configuration is automatic.** The default model is set in `.claude/settings.json`, and each sub-agent's `model:` frontmatter uses Claude aliases (`fable`, `opus`, `sonnet`, `haiku`) that automatically resolve to the latest available versions (currently Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 4.5 on the Anthropic API; other providers may resolve earlier versions). You don't need to edit model names manually. Doctrine last verified against Claude Code **v2.1.288** (2026-10-03).

> **Optional check after hand edits.** On Claude Code 2.1.283 or newer, `/doctor prompt-audit` audits `CLAUDE.md`, agents, skills and commands for prompt patterns written for older models — useful after you customise HiveSmith or a generated swarm.

> **File access is native.** Claude Code's built-in `Read`/`Write`/`Edit`/`Bash` tools (governed by its permission system) handle all filesystem work — no filesystem MCP server is needed or used.

## Project Structure

```
HiveSmith/
├── CLAUDE.md                          # Orchestrator system prompt (plain markdown)
├── README.md
├── LICENSE
├── .gitignore
├── .mcp.json                          # Project-scoped MCP servers (optional search fallback)
├── research-archive/                  # Frozen research corpus from past generation runs (not live config)
└── .claude/
    ├── settings.json                  # Default model, MCP allowlist + guard-hook wiring
    ├── hooks/
    │   └── block-destructive.py       # PreToolUse guard: deterministic Destructive Action Barrier
    ├── rules/                         # Auto-loaded global rules
    │   ├── 01-web-search-mandatory.md
    │   ├── 02-destructive-action-barrier.md
    │   ├── 03-agent-as-code-standard.md
    │   ├── 04-prompt-injection-shield.md
    │   ├── 05-idempotency-and-state.md
    │   ├── 06-human-in-the-loop.md
    │   ├── 07-conflict-resolution.md
    │   ├── 08-blueprint-schema.md
    │   └── 09-swarm-quality-doctrine.md
    └── agents/                        # 15 sub-agent definitions
        ├── dag-validator.md
        ├── domain-architect.md
        ├── mcp-integrator.md
        ├── persona-engineer.md
        ├── prompt-evaluator.md
        ├── qa-validator.md
        ├── repo-analyzer-worker.md
        ├── researcher-academic-independent.md
        ├── researcher-anthropic-openai.md
        ├── researcher-google-cloud.md
        ├── researcher-security.md
        ├── researcher-tech-stack.md
        ├── researcher-vcs-github.md
        ├── safety-engineer.md
        └── tool-smith.md
```

Generated swarms follow the same layout: a plain-markdown `CLAUDE.md` orchestrator, sub-agents in `.claude/agents/`, auto-loaded rules in `.claude/rules/`, model config in `.claude/settings.json`, and — only when external capabilities are needed — a project-root `.mcp.json`. When a swarm's core job is a repeatable fan-out with cross-verification, it can also ship a saved [dynamic workflow](https://code.claude.com/docs/en/workflows) in `.claude/workflows/`.

## Global Rules

All agents (both HiveSmith's own and any it generates) operate under 9 global rules:

1. **Web Search Mandatory** — No hallucinated packages, versions, or configs
2. **Destructive Action Barrier** — No `rm -rf`, `DROP TABLE`, or cloud deletions without human approval; enforced by a deterministic `PreToolUse` guard hook, not just prose
3. **Agent-as-Code Standard** — The canonical Claude Code schema: file formats, frontmatter keys, context inheritance, hooks doctrine, coordination mechanisms (hub-and-spoke by allowlist, agent teams, dynamic workflows), model routing and the generated-swarm tier budget — single source of truth for the whole workspace
4. **Prompt Injection Shield** — All external inputs treated as untrusted
5. **Idempotency & State Safety** — Operations must be safe to re-run
6. **Human-in-the-Loop** — Agents pause and ask when facing critical ambiguity
7. **Conflict Resolution** — Orchestrator resolves inter-agent disagreements; safety wins by default
8. **Blueprint Schema** — Enforced JSON structure for all swarm blueprints, including per-agent decomposition justification, shared-state and hook sections
9. **Swarm Quality Doctrine** — Anthropic's guidance and published research encoded as hard checks: single-agent justification, context-boundary (not phase) decomposition, ~200-line prompt budgets, verifier hardening, just-in-time context, instruction files written for current models

## Contributing

Contributions are welcome. If you have ideas for new agent types, improved safety rules, or better research strategies, feel free to open an issue or submit a pull request.

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

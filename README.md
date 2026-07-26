# 🐝⚒️ HiveSmith

**You describe the swarm. HiveSmith forges it.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Powered by](https://img.shields.io/badge/Powered_by-Claude_Code-8b5cf6.svg)](https://claude.ai)
[![Agents](https://img.shields.io/badge/Sub--Agents-19-orange.svg)](#agent-roster)

A meta-agent system that designs and generates production-ready multi-agent swarms. Built for the [Claude Code](https://claude.ai) CLI ecosystem.

You describe what you need. HiveSmith researches the domain, architects the agent hierarchy, writes every prompt and config file, validates the topology, and delivers a working swarm — ready to run with `claude`.

> **HiveSmith** — the smith that forges hives. Sister project of [SwarmForge](https://github.com/Sh3rm/SwarmForge) (the Gemini/Antigravity edition): same architecture, same 19 agents, same 7-step pipeline — rebuilt from the ground up on Claude Code's native primitives: sub-agents, auto-loaded rules, and project MCP config.

## How It Works

HiveSmith is itself a swarm. An orchestrator (`CLAUDE.md`) coordinates 19 specialized sub-agents — each a real Claude Code sub-agent with its own isolated context window, tool allowlist, and model tier — through a 7-step pipeline:

```
1. Information Gathering    — Apply model routing, spawn domain researchers in parallel
2. Synthesis                — Merge raw research into a unified architectural baseline
3. Architecture             — Design the swarm blueprint with tier-based model routing
4. Infrastructure & Safety  — Generate MCP configs, safety rules, telemetry, custom tools
5. Context Optimization     — Compress the payload without losing architectural logic
6. Persona Generation       — Write CLAUDE.md, .claude/agents/*.md, rules, and settings to disk
7. Evaluation & QA          — Simulate edge cases, validate DAG topology, verify dependencies
```

If QA or DAG validation finds issues, the pipeline loops back for refinement automatically.

## Key Design Decisions

- **Native Claude Code Sub-Agents.** Every worker persona is a `.claude/agents/<name>.md` file with the official frontmatter schema (`name`, `description`, `tools`, `model`). The orchestrator delegates through Claude Code's Agent tool, so each worker runs in an isolated context window with a least-privilege tool allowlist enforced by the harness itself — researchers can search but not write, validators can read but not modify.

- **Tier-Based Model Routing.** HiveSmith assigns models using Claude aliases (`fable`, `opus`, `sonnet`, `haiku`) based on cognitive load. Heavy reasoning and orchestration gets `fable` (Fable 5), complex coding gets `opus` (Opus 5), research gets `sonnet` (Sonnet 5), fast scanning gets `haiku` (Haiku 4.5). When Anthropic ships new models, the aliases resolve to the latest versions automatically.

- **Research Before Architecture.** Every generated swarm includes its own researcher agents. HiveSmith never relies on pre-trained knowledge for domain-specific decisions. It searches the web first, every time — via Claude Code's native `WebSearch`/`WebFetch` tools, with an optional tokenless [duckduckgo-mcp-server](https://pypi.org/project/duckduckgo-mcp-server/) fallback in `.mcp.json`.

- **Strict QA.** The `qa-validator` checks the generated frontmatter schemas against Claude Code's real spec (and rejects foreign fields), verifies model aliases, runs dependency pre-flights (`uv`, `npx`), and validates directory structure before anything ships.

## Agent Roster

All 19 sub-agents live in `.claude/agents/`:

| Agent | Role | Default Tier |
|---|---|---|
| `domain-architect` | Designs swarm topology with benchmark-driven model selection | Fable |
| `persona-engineer` | Writes all system prompts (CLAUDE.md, .claude/agents/*.md) | Fable |
| `prompt-evaluator` | Simulates edge cases against generated prompts | Fable |
| `safety-engineer` | Generates domain-specific safety rules | Fable |
| `tool-smith` | Builds custom scripts when standard MCP tools aren't enough | Fable |
| `memory-manager` | Designs shared context and persistence layers | Fable |
| `researcher-synthesizer` | Merges all research into a single baseline | Fable |
| `context-optimizer` | Compresses payloads without losing architectural logic | Sonnet |
| `mcp-integrator` | Generates the project-root `.mcp.json` for the target swarm | Sonnet |
| `dag-validator` | Validates swarm topology — detects cycles, orphan agents, broken links | Sonnet |
| `telemetry-architect` | Designs logging, tracing, and metrics standards | Sonnet |
| `researcher-google-cloud` | Google Cloud, Gemini best practices | Sonnet |
| `researcher-anthropic-openai` | Anthropic & OpenAI multi-agent patterns | Sonnet |
| `researcher-tech-stack` | Version verification, deprecation checks | Sonnet |
| `researcher-security` | OWASP, HITL, guardrail best practices | Sonnet |
| `researcher-academic-independent` | arXiv, independent AI research blogs | Sonnet |
| `researcher-vcs-github` | Mines GitHub/GitLab for existing agent configs | Sonnet |
| `repo-analyzer-worker` | Fast concurrent scanning of cloned repos | Haiku |
| `qa-validator` | Schema validation, dependency checks, pass/fail reporting | Haiku |

> "Default Tier" is set in each agent's `model:` frontmatter and applied automatically by Claude Code. The orchestrator can steer overrides at runtime based on task complexity.

## 🚀 Quick Start

HiveSmith is powered by [Claude Code](https://claude.ai).

**1. Prerequisites:**

- **[Claude Code CLI](https://claude.ai)** — installed and authenticated (`claude` command available)
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

> **Model configuration is automatic.** The default model is set in `.claude/settings.json`, and each sub-agent's `model:` frontmatter uses Claude aliases (`fable`, `opus`, `sonnet`, `haiku`) that automatically resolve to the latest available versions (currently Fable 5, Opus 5, Sonnet 5, Haiku 4.5). You don't need to edit model names manually.

> **File access is native.** Claude Code's built-in `Read`/`Write`/`Edit`/`Bash` tools (governed by its permission system) handle all filesystem work — no filesystem MCP server is needed or used.

## Project Structure

```
HiveSmith/
├── CLAUDE.md                          # Orchestrator system prompt (plain markdown)
├── README.md
├── LICENSE
├── .gitignore
├── .mcp.json                          # Project-scoped MCP servers (optional search fallback)
└── .claude/
    ├── settings.json                  # Default model + project settings
    ├── rules/                         # Auto-loaded global rules
    │   ├── 01-web-search-mandatory.md
    │   ├── 02-destructive-action-barrier.md
    │   ├── 03-agent-as-code-standard.md
    │   ├── 04-prompt-injection-shield.md
    │   ├── 05-idempotency-and-state.md
    │   ├── 06-human-in-the-loop.md
    │   ├── 07-conflict-resolution.md
    │   └── 08-blueprint-schema.md
    └── agents/                        # 19 sub-agent definitions
        ├── context-optimizer.md
        ├── dag-validator.md
        ├── domain-architect.md
        ├── mcp-integrator.md
        ├── memory-manager.md
        ├── persona-engineer.md
        ├── prompt-evaluator.md
        ├── qa-validator.md
        ├── repo-analyzer-worker.md
        ├── researcher-academic-independent.md
        ├── researcher-anthropic-openai.md
        ├── researcher-google-cloud.md
        ├── researcher-security.md
        ├── researcher-synthesizer.md
        ├── researcher-tech-stack.md
        ├── researcher-vcs-github.md
        ├── safety-engineer.md
        ├── telemetry-architect.md
        └── tool-smith.md
```

Generated swarms follow the same layout: a plain-markdown `CLAUDE.md` orchestrator, sub-agents in `.claude/agents/`, auto-loaded rules in `.claude/rules/`, model config in `.claude/settings.json`, and — only when external capabilities are needed — a project-root `.mcp.json`.

## Global Rules

All agents (both HiveSmith's own and any it generates) operate under 8 global rules:

1. **Web Search Mandatory** — No hallucinated packages, versions, or configs
2. **Destructive Action Barrier** — No `rm -rf`, `DROP TABLE`, or cloud deletions without human approval
3. **Agent-as-Code Standard** — Claude Code native file formats, least-privilege tool allowlists, dynamic model routing
4. **Prompt Injection Shield** — All external inputs treated as untrusted
5. **Idempotency & State Safety** — Operations must be safe to re-run
6. **Human-in-the-Loop** — Agents pause and ask when facing critical ambiguity
7. **Conflict Resolution** — Orchestrator resolves inter-agent disagreements; safety wins by default
8. **Blueprint Schema** — Enforced JSON structure for all swarm blueprints

## Contributing

Contributions are welcome. If you have ideas for new agent types, improved safety rules, or better research strategies, feel free to open an issue or submit a pull request.

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

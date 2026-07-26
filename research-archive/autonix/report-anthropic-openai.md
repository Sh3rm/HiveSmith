# Anthropic & OpenAI Agentic Architecture Report (2026-07-26, researcher-anthropic-openai)

## CRITICAL: Claude Code sub-agent schema expanded (v2.1.2xx, July 2026)
Docs moved: docs.anthropic.com/en/docs/claude-code/* → **code.claude.com/docs/en/***.
Frontmatter — Required: `name` (lowercase+hyphens, matches filename, 3–50 chars), `description` (drives auto-delegation).
Optional (ALL documented): `tools` (list or comma string; also `Agent(agent_type)` syntax), `disallowedTools`, `model` (sonnet/opus/haiku/fable/full-ID/inherit — **default inherit**; Anthropic recommends inherit unless specific capability needed), `permissionMode` (default/acceptEdits/auto/dontAsk/bypassPermissions/plan), `maxTurns`, `skills` (preloaded), `mcpServers`, `hooks`, `memory` (user/project/local), `background`, `effort` (low/medium/high/xhigh/max), `isolation` (worktree), `color`, `initialPrompt`.
- Antigravity fields still forbidden (max_output_tokens, enable_write_tools, enable_mcp_tools, enable_subagent_tools, planning-mode). Note confusable: `permissionMode: plan` is REAL; `planning-mode` is not.
- Anthropic authoring rules (official agent-development skill): description template "Use this agent when [conditions]. Typical triggers include [2–4 scenarios]"; body in second person, numbered responsibilities, explicit output format; target 500–3,000 chars; least-privilege tools.
- **Sub-agents CANNOT spawn sub-agents** (Agent tool withheld; `tools: Agent(x)` only works for main-thread `claude --agent`). Hard-validates single-level orchestrator-worker.
- `.claude/agents/` scanned recursively (subfolders OK). `.claude/rules/` confirmed real; recursive; **`paths:` frontmatter rules load on-demand** (context saving). Import syntax `@path`.
- Hooks: 24+ events (PreToolUse, PostToolUse, Stop, SubagentStart/Stop, ConfigChange, WorktreeCreate…). PreToolUse exit 2 blocks call, stderr fed back to Claude. Stop exit 2 blocks completion. Anthropic steering blog (2026-06-18): "Don't use instructions for absolute restrictions… use deterministic tools instead."
- **Agent Teams (2026): experimental, env-gated, DO NOT use for delivered swarm** — ship subagents; mention teams as opt-in escalation only.
- Skills = procedural packs loaded into main thread; NOT agent personas. Compose: agent can preload skills.

## Anthropic multi-agent patterns
- Building Effective Agents: prompt chaining / routing / parallelization (sectioning+voting) / orchestrator-workers / **evaluator-optimizer** (best with clear eval criteria). Simplicity first; invest in tool design.
- Multi-agent research system: 3–5 parallel subagents (>10 only for clearly divided work); MAS ~15× chat tokens; token spend explains 80% variance; orchestrator prompt must carry objective, output format, tool guidance, clear boundaries, **effort-scaling rules**; checkpoint+resume; near context limit → summarize to external memory, spawn fresh subagents.
- **C compiler post (highest-signal for building swarms)**: "scaffolding over orchestration" — file-based task locks, progress docs, failing tests as coordination signals. **"The task verifier must be nearly perfect."** CI gate: commits can't break existing functionality. Sampled test runs (1–10%) during iteration, full suite at gate. Grep-friendly error logs (reason on same line as ERROR), few lines to stdout + full logs to file. 16 parallel agents → diminishing returns; task granularity must match agent count.
- Agent SDK loop: gather context → act → **verify** (rules-based preferred > visual feedback [BUI screenshots] > LLM judge).
- Best practices: Explore→Plan→Code→Commit; "give Claude something that produces pass/fail and the loop closes itself"; **writer/reviewer separation** (fresh context removes self-bias — reviewer defines own standards); git worktrees for parallel sessions; CLAUDE.md removal test per line — **oversized CLAUDE.md is a named failure mode**; reset after two repeated corrections.

## Model lineup & routing (July 2026, first-party)
Aliases: default, best (Fable 5 else Opus), fable (complex long-running), opus (complex reasoning), sonnet (daily coding), haiku (simple/fast), sonnet[1m]/opus[1m], opusplan. Effort: low/medium/high (default)/xhigh/max — settable via `effort:` frontmatter or settings `effortLevel`. `CLAUDE_CODE_SUBAGENT_MODEL` env can override frontmatter.
Selection guidance (2026-07-07 blog): Sonnet = precisely describable edits/mechanical; Opus/Fable = subtle bugs, ambiguity, architecture, multi-step; effort controls files read/verification depth/steps. Diagnostic: confidently wrong → upgrade model; skipped verification → raise effort.
Pricing (3rd-party, directional): Fable 5 $10/$50, Opus 5 $5/$25, Sonnet 5 $2/$10 intro, Haiku 4.5 $1/$5. Fable may carry weekly usage caps — don't assign `fable` broadly.
Recommended AutoNix tiering: orchestrator opus/high; architect fable-or-opus/xhigh; implementers opus/high; test-engineer sonnet/high; reviewers opus/high; lint-scan haiku/low.

## OpenAI transferable lessons
1. **Anti-bloat: "Start with one agent whenever you can; add specialists only when they materially improve capability isolation, policy isolation, prompt clarity, or trace legibility."**
2. Manager pattern (central coordination) is the ONLY pattern Claude Code supports (no nesting/peer messaging).
3. Layered guardrails: LLM checks + rules-based + moderation; single layer insufficient. Claude Code equivalent: PreToolUse hooks + tools/disallowedTools + permissionMode.
4. Guardrail scoping: orchestrator-level rules don't protect subagent tool calls — put hooks at the tool layer.
5. Code-orchestration over LLM-orchestration when predictability matters.

## Dev-team swarm practices
- Roster: "most teams settle on a handful of well-scoped agents"; concurrency 3–5; every agent beyond ~7 needs explicit independent-workstream justification.
- NOT-a-subagent cases: sequential dependent chains; concurrent edits to same file; small tasks; work needing negotiation.
- Description = the delegation router: trigger conditions, not capability nouns; "use proactively"; 2–4 named scenarios.
- Writer/reviewer: reviewer `tools: Read, Grep, Glob, Bash` + `disallowedTools: Write, Edit`; opus tier.
- Verification: Stop hook exit 2 when gate fails (deterministic completion block); PostToolUse hook auto-running gofmt/go vet after Edit.
- **Manifesto pattern CONFIRMED necessary**: subagents never inherit conversation; each Task prompt self-contained (objective, EL matrix, file ownership, output format, effort scaling). CLAUDE.md IS auto-loaded by subagents — shared invariants go there, kept lean.
- Parallel safety: file-ownership boundaries per agent; `isolation: worktree` on implementers (isolated repo copy, auto-cleaned).

## Directly applicable pattern list (condensed)
1. Single-level orchestrator-worker; workers never delegate (physically enforced).
2. Roster 6–7, concurrency 3–5: linux-domain-researcher, go-architect, cli-tui-developer, bui-developer, test-engineer, code-reviewer, release-packager.
3. Split CLI/TUI vs BUI by file ownership; don't split further (same-file conflict anti-pattern).
4. `isolation: worktree` on implementer agents.
5. Reviewer with hard tool boundaries + fresh context.
6. Evaluator-optimizer wired as deterministic gate: `go build && go vet && gofmt -l && go test -race` as Stop hook.
7. **Verifier lands first** — test harness + CI gate before feature agents run.
8. Explore→Plan→Code→Commit; `permissionMode: plan` on architect.
9. Tiering via `effort:` field, not prose.
10. Descriptions with 2–4 concrete triggers.
11. Manifesto per delegation (objective, boundaries, output format, effort rule).
12. Deterministic guardrails (PreToolUse deny hook) over prose rules.
13. Path-scoped rules (`paths: "**/*.go"`, `paths: "packaging/**"`) for on-demand loading.
14. Lean CLAUDE.md (removal test per line).
15. Budget ~15× tokens; haiku/sonnet on high-volume roles.
16. Ship subagents, NOT experimental Agent Teams.

## Schema corrections HiveSmith itself must apply (relay to user)
- Rule 03's "exactly these keys" is outdated → treat 4-key list as minimum; allow effort/isolation/disallowedTools/permissionMode/maxTurns/skills/mcpServers/hooks/memory/background/color/initialPrompt.
- qa-validator must not reject the new fields; keep rejecting Antigravity fields.
- Accept tools as YAML list or comma string.
- Rewrite doc links to code.claude.com/docs/en/*.
- `model: inherit` is the documented default & recommendation.

(Key sources: code.claude.com/docs/en/{sub-agents,agent-teams,memory,model-config,best-practices,hooks-guide}; anthropic.com research/engineering posts; claude.com blogs 2026-04-07, 2026-06-18, 2026-07-07; OpenAI agents SDK docs + practical guide PDF.)

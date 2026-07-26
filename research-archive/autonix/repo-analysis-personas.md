# Repo Analysis — Agent Persona Patterns (voltagent-subagents + wshobson-agents)

## voltagent findings
- All agents share one monolithic template. golang-pro frontmatter: name/description ("Use when building Go applications requiring…")/tools: Read, Write, Edit, Bash, Glob, Grep/model: sonnet.
- Good: "Use when…" action-oriented descriptions naming concrete triggers. Weakness: some stack 3-4 trigger clauses into run-ons, diluting delegation.
- **RED FLAG — reject:** `## Communication Protocol` JSON blocks (requesting_agent / "context manager" queries / status telemetry) describe a pub-sub runtime that DOES NOT EXIST in Claude Code's Task model. Copying = Constraint 11 violation.
- Also reject: fabricated numeric checklists ("Deployment frequency > 10/day"), canned "Delivery notification" marketing prose, 8-12 flat capability-laundry sections, "Integration with other agents" cross-reference lists (duplicates DAG).

## wshobson findings
- Plugin layout: plugins/<name>/{agents/, commands/, skills/<skill>/{SKILL.md, references/details.md}}.
- **Progressive disclosure works mechanically**: SKILL.md short (~90-165 lines) + deep refs (549 lines go-concurrency) pulled on demand. Skills auto-discovered via own name/description frontmatter; NO explicit agent→skill wiring found.
- SKILL.md skeleton: title → When to Use (6 bullets) → Core Concepts → Quick Start (one runnable block) → pointer to references/details.md → Do's/Don'ts (5 each, bold lead-in + rationale).
- Their golang-pro has NO tools field (inherits all — violates our least-privilege rule, don't copy). Their test-automator (41 lines) shows the tightest skeleton: Purpose → Capabilities (bold-lead-in bullets) → Response Approach (numbered verbs) → **Output Format** (concrete deliverable shape).
- ⚠ wshobson name-doesn't-match-filename convention (plugin-prefixed names) conflicts with our rule 03 — do NOT copy.

## Clarity vs bloat correlation
KEEP: "When invoked" numbered protocol; verifiable checklists tied to real artifacts (gofmt passes, not invented SLAs); **Output Contract section**; single-condition trigger descriptions; progressive disclosure (short persona + deep reference docs).
REJECT: capability laundry lists; fictitious runtime protocols; invented metrics; behavioral-trait adjective lists; example-interaction sections (low value/token).

## Recommended AutoNix persona skeleton
```yaml
---
name: <exact-filename>
description: Use this agent when <single concrete trigger, one sentence>.
tools: <least-privilege allowlist>
model: <tier per doctrine>
---
You are <role>, a senior <domain> engineer on the AutoNix team building Go-based Linux automation for EL 8/9/10. <1-2 sentences, no marketing.>

## When Invoked
1. <concrete first actions — read specific files/state>

## Responsibilities
- <bold-lead-in>: <one clarifying clause> (5-8 bullets max)

## Checklist / Definition of Done
- <verifiable real criteria only>

## Output Contract
<files written, report format handed back to orchestrator>

## Handoff
Delegates to / receives from: <1-3 roster agents matching workflow_dag edges>
```
Deep domain material (libvirt XML notes, EL specifics) → separate reference docs / path-scoped rules, not persona body.

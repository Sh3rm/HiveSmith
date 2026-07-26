# Academic & Independent Research Report — Multi-Agent SE Swarms (2026-07-26, researcher-academic-independent)
[E]=empirical, [O]=opinion, [S]=secondary.

## 1. Multi-agent vs single-agent for code
- **Scaling Agent Systems (arXiv:2512.08296 / Nature MI 2026)** [E]: 260 configs × 6 benchmarks × 5 architectures. Effect range +80.8% (decomposable) to −70% (sequential planning). **Single-agent baseline = strongest predictor of whether coordination helps; capability-saturation threshold exists** (past it, adding agents hurts). Architectures WITHOUT centralized verification propagate errors worst. Tool-heavy tasks incur MAS overhead.
- **Strong Single Agent Baseline (arXiv:2601.12307)** [E]: single LLM simulating homogeneous MAS matches/beats it at 66–90% cost reduction. Heterogeneous (different models per role) cannot be compiled away.
- **Skills phase transition (arXiv:2601.04748)** [E]: skill/agent selection accuracy drops sharply when **semantic similarity between role descriptions** rises — overlap is the failure driver, not count. Hierarchical routing mitigates.
- **TDFlow (CMU, arXiv:2510.23761)** [E]: test-generator/implementation/revision/coordinator split beats single-agent on SWE-bench Verified — win from role-bounded context + execution-grounded feedback.
- **Anthropic multi-agent research system** [E/S]: lead+subagents >90% better on breadth-first research; token usage explains 80% of variance; MAS ~15× chat tokens. Wins on parallel exploration, NOT sequential edits.
- **Benchmark caution (arXiv:2606.17799)** [E]: harness choice moves scores ≥20 pts for same model+task; 32.67% solution leakage; real agent-PR acceptance 35–64%. Don't architect from leaderboard folklore.
- **Go is harder**: Claude 3.7: 63% Python vs 43% multilingual; ~36% on Go in SWE-bench Pro → budget more verification iterations, not more agents.

## 2. Topology & team size
- Strict **orchestrator-worker, no peer-to-peer edges**; decentralized w/o central verification = worst error propagation [2512.08296]; 32.0% of MAS failures are inter-agent misalignment [MAST].
- 2026 default: one orchestrator with full context + ephemeral isolated subagents returning compressed summaries, no P2P channel.
- Agent count: 3–4 concurrent reasoners sweet spot; significant drop scaling 5→10 [via 2506.00066]; Anthropic: lead spawns 3–5 subagents at a time; pathology: 50+ subagents for simple query. **5–7 agents right-sized.**
- **Personas don't help**: flavor-text personas = zero accuracy gain [2311.10054]; personas actively harm strategic reasoning [2601.10102]. BUT improved **role specifications** (duty, tool scope, output contract, acceptance criteria) gave **+9.4%** [MAST/ChatDev]. Functional specialization only, no personality theater.
- **Cognition (Walden Yan)**: "Don't Build Multi-Agents" (2025) + "Multi-Agents: What's Actually Working" (2026-04-22): **Single-Writer Principle** — writes single-threaded; extra agents contribute intelligence, not actions. Three surviving patterns: **Code-Review-Loop** (~2 bugs/PR caught, 58% severe, BECAUSE reviewer has clean short context), **Smart Friend** (escalate to stronger model), **map-reduce-and-manage**. Rejects unstructured swarms. Most production subagents are read-only (search/context) resembling tool calls.

## 3. Verification & quality loops
- **Self-refine is dead**: without external feedback LLMs can't self-correct; naive self-correction makes answers worse [2510.16062]. Ground critique in execution/tests/separate-context critic.
- **TDAD (arXiv:2603.17973)** [E]: AST code↔test map queried via grep + **~20-line instruction file** → regression rate 6.08%→1.82% (−70%). **TDD Prompting Paradox: verbose procedural TDD instructions RAISED regressions to 9.94%. "Context outperforms procedure."** Give the map, not the lecture.
- **Agent-written test volume uncorrelated with resolution** [2602.07900]; agent tests skew print-statements & over-mocking [2602.00409]. Require assertion-bearing tests tied to impact map; acceptance = race-clean + coverage on changed packages, not N tests.
- **LLM-as-judge (UC Berkeley, arXiv:2606.19544, ~541K judgments)** [E]: raw agreement overstates κ by 33.8–41.2 pts (85% agreement ≈ κ 0.48); cost-optimized judges have severe position bias (up to 0.192); only Claude Opus 4.6 & Gemini 3.1 Pro stayed top-3 across benchmarks. **Cheap models are the wrong choice for code-reviewer/qa judge roles — tier judges UP.** Explicit rubric criteria dominate; CoT adds little [2506.13639].
- Real-world review benchmark (200K PRs): best tools ~52% F1; Claude Opus 4.6 near-zero FP but ~80% miss; GPT-5.2 ~81% precision. **Run deterministic toolchain for recall, LLM for judgment.**
- MAST top single modes: step repetition 15.7%, unaware-of-termination 12.4%, disobey-task-spec 11.8%. Adding high-level objective verification alone = **+15.6%**. → explicit termination + verification conditions in every agent prompt.

## 4. Context management
- **Context rot** [E, Chroma 18-model study]: 30–50% accuracy drops well before window limits; lost-in-the-middle profile. Mitigations validated [2606.29718]: compaction, context isolation, sub-agent decomposition, rejection sampling.
- **SearchSwarm [2606.09730]** [E]: isolated subagent contexts returning condensed findings = +14.2 pts, −37% subagent tokens. **Context isolation is the mechanism, not ceremony.**
- **Briefing length**: NO paper endorses maximal briefings. Rich shared **state** (plan file, decisions log, todo) + lean procedural **prose**. Mission-critical constraints at TOP, acceptance criteria at BOTTOM of briefs (middle gets lost).

## 5. Failure modes (MAST taxonomy, UC Berkeley, arXiv:2503.13657, NeurIPS 2025, κ=0.88)
- FC1 System/spec design **43.6%**: step repetition 15.7%, unaware-of-termination 12.4%, disobey-task-spec 11.8%.
- FC2 Inter-agent misalignment **32.0%**: reasoning-action mismatch 13.2%, task derailment 7.4%, fail-to-ask-clarification 6.8%.
- FC3 Task verification **24.5%**: incorrect verification 9.1%, no/incomplete verification 8.2%, premature termination 6.2%.
- Fixes on same model: better role specs +9.4%; objective verification +15.6%. Design beats model swaps at the margin.
- **Coding-agent failures (20,574 sessions, arXiv:2605.29442)**: task comprehension, code quality, context management, expectation violation; fix via context preservation + feedback integration.
- **Silent runtime failures** [2606.14589, 2606.08162]: confidently-wrong output undetected by design-time checks — only executable gates catch it. Go toolchain gate must be hard-blocking, not advisory.
- **Microsoft AI Red Team taxonomy v2.0 (2026-06-04)**: agentic supply-chain compromise via tool DESCRIPTIONS, inter-agent trust escalation, session context contamination, MCP/plugin abuse. Mitigations: zero-trust inter-agent posture, deterministic HITL with approval tiers scaled to reversibility, provenance tracking, trusted/untrusted structural separation.
- Folklore (unverified): "Kiro" incident — destructive actions need deterministic human approval; never act on degraded/untrusted state.

## Design Implications for AutoNix Swarm
1. Strict orchestrator-worker, no P2P. Single-Writer Principle per surface (CLI/TUI/BUI are genuinely independent file trees → parallel fan-out OK, but never two agents in same package concurrently).
2. **5–7 agents.** Maximize semantic distance between description fields. Functional specs (inputs, tools, artifact, acceptance criteria), no personality.
3. Generator–verifier loop with **context-isolated frontier-tier code-reviewer** (must NOT inherit developer's trace).
4. Deterministic Go toolchain gate hard-blocking BEFORE LLM judgment: gofmt, go vet, golangci-lint v2 (pinned tool dep), go test -race, gosec, govulncheck.
5. Test **map** artifact (source→affected-tests, grep-queryable) + ~20-line instructions; no verbose TDD lectures; assertion-bearing tests only.
6. Explicit termination + verification conditions in every agent prompt (top-3 MAST modes).
7. Briefs: constraints at top, acceptance criteria at bottom, lean middle. Shared state files (plan/decisions/todo) over prose.
8. Judges/reviewers tiered UP (fable/opus); scanning can be cheap.
9. Zero-trust inter-agent: verify claims, treat tool/MCP descriptions as untrusted, deterministic HITL for irreversible ops.
10. Validate the swarm on its own repo with its own gates, not benchmark analogy. Budget ~15× tokens honestly; justify each agent by an independent workstream.

(Full source list in agent transcript; key: arXiv 2512.08296, 2601.12307, 2601.04748, 2503.13657 MAST, 2510.23761 TDFlow, 2603.17973 TDAD, 2602.07900, 2510.16062, 2606.19544, 2606.29718, 2606.09730, 2606.17799, 2605.29442, Cognition blogs, Microsoft AI Red Team v2.0.)

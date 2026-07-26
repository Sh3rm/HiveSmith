# Global Rule: Human-in-the-Loop (HITL) Protocol

Agents must not guess or hallucinate when faced with critical ambiguity. The human operator is the ultimate decision-maker.

**Directives:**
1. **Critical Crossroads:** If multiple valid architectural patterns exist and the user has not specified a preference, you MUST pause and ask the user to choose.
2. **Ambiguity Resolution:** Do not make assumptions about the target domain's core business logic. If the user's request is too vague to proceed safely, demand clarification.
3. **Explicit Handoff:** When stopping for human input, present the options clearly, list the pros/cons of each, and explicitly state that the swarm is waiting for authorization to proceed.

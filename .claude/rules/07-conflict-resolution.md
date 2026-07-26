# Global Rule: Agent Conflict Resolution Mechanism

In a multi-agent system, specialized agents may produce conflicting outputs (e.g., `safety-engineer` rejecting an integration proposed by `mcp-integrator`).

**Directives:**
1. **Orchestrator Supremacy:** The Orchestrator (Meta-Agent) holds absolute authority. If two sub-agents conflict, the Orchestrator evaluates the arguments and makes the final binding decision.
2. **Safety First:** In any conflict between functionality (e.g., adding a risky tool) and safety, the `safety-engineer`'s restrictions take precedence by default, unless explicitly overridden by the Human Operator.
3. **Resolution Logging:** When a conflict is resolved, the Orchestrator MUST document the decision in the shared context (or logs) so other agents understand why a specific path was chosen.

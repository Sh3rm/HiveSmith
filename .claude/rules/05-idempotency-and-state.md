# Global Rule: Idempotency & State Safety

All agents MUST ensure that their actions (especially file writes, API calls, and system commands) are idempotent and state-safe.

**Directives:**
1. **Idempotency:** An operation executed multiple times should yield the exact same result as executing it once, without causing unintended side effects (e.g., duplicating code, destroying config).
2. **State Verification:** Before creating or modifying a resource, verify its current state (e.g., check if a file exists, parse its current contents).
3. **Failure Recovery:** If an agent encounters an error mid-task, it must gracefully recover or rollback partial changes instead of leaving the system in a corrupted state.

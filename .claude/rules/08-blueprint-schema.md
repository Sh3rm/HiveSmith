# Global Rule: Swarm Blueprint JSON Schema

To ensure perfect interoperability, the `domain-architect` MUST always output the swarm design using the following strict JSON schema.

**Required JSON Structure:**
```json
{
  "swarm_name": "string",
  "version": "string",
  "domain": "string",
  "single_agent_justification": "string (REQUIRED — why one well-tooled agent cannot do this job: context pollution, true parallelism, or specialization threshold; multi-agent systems cost 3-15x tokens, so the burden of proof is on decomposition)",
  "agents": [
    {
      "id": "string",
      "role": "string",
      "model": "string ('fable', 'opus', 'sonnet', 'haiku', or 'inherit' — maps 1:1 to the agent frontmatter `model` key; never a full model version string)",
      "tools_required": ["string"],
      "dependencies": ["string"],
      "effort": "string (OPTIONAL — 'low'|'medium'|'high'|'xhigh'|'max'; only when the role's reasoning depth deviates from the session default)",
      "isolation": "string (OPTIONAL — 'worktree'; only for agents writing files inside the same git repo in parallel with other writers)",
      "maxTurns": "number (OPTIONAL — runaway cap for loop-prone workers)",
      "memory": "string (OPTIONAL — 'user'|'project'|'local'; only for agents whose judgment improves across runs)"
    }
  ],
  "hooks": [
    {
      "event": "string (OPTIONAL section — e.g. 'PreToolUse'; guard hooks the swarm ships in .claude/settings.json, per Rule 02 §4)",
      "type": "string ('command'|'prompt'|'agent'|'http'|'mcp_tool')",
      "purpose": "string",
      "matcher_or_pattern": "string"
    }
  ],
  "mcpServers": {
    "stdio_server_name": {
      "command": "string",
      "args": ["string"],
      "env": {}
    },
    "remote_server_name": {
      "type": "http",
      "url": "string",
      "headers": {}
    }
  },
  "workflow_dag": {
    "edges": [
      {"from": "string", "to": "string"}
    ]
  }
}
```
*No deviation from this top-level key structure is permitted. The `hooks` top-level section and the per-agent `effort`/`isolation`/`maxTurns`/`memory` keys are OPTIONAL — omit them entirely when not needed; when present they must follow the shapes above.*

**`mcpServers` semantics (mirrors the official `.mcp.json` format 1:1, so `mcp-integrator` can emit entries verbatim):** local stdio servers use `command`/`args`/`env` (the `type` field is optional for them — Claude Code treats a typeless entry as stdio); remote servers use `url` and MUST carry an explicit `"type"` of `http` (preferred), `sse` (deprecated), or `ws` — a `url` entry without `type` is a configuration error that Claude Code skips at load time. Include only the entry shape actually needed; both are shown above for reference.

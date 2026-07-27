# Global Rule: Swarm Blueprint JSON Schema

To ensure perfect interoperability, the `domain-architect` MUST always output the swarm design using the following strict JSON schema.

**Required JSON Structure:**
```json
{
  "swarm_name": "string",
  "version": "string",
  "domain": "string",
  "agents": [
    {
      "id": "string",
      "role": "string",
      "model": "string ('fable', 'opus', 'sonnet', 'haiku', or 'inherit' — maps 1:1 to the agent frontmatter `model` key; never a full model version string)",
      "tools_required": ["string"],
      "dependencies": ["string"]
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
*No deviation from this top-level key structure is permitted.*

**`mcpServers` semantics (mirrors the official `.mcp.json` format 1:1, so `mcp-integrator` can emit entries verbatim):** local stdio servers use `command`/`args`/`env` (the `type` field is optional for them — Claude Code treats a typeless entry as stdio); remote servers use `url` and MUST carry an explicit `"type"` of `http` (preferred), `sse` (deprecated), or `ws` — a `url` entry without `type` is a configuration error that Claude Code skips at load time. Include only the entry shape actually needed; both are shown above for reference.

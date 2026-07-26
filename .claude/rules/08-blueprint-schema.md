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
  "mcp_servers": {
    "server_name": {
      "command": "string",
      "args": ["string"],
      "env": {}
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

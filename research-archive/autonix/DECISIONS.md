# AutoNix — User-Ratified Architecture Decisions (HITL, 2026-07-26)

1. **libvirt binding: pure-Go `digitalocean/go-libvirt` (vendored/pinned) + `libvirt.org/go/libvirtxml`**, behind internal Hypervisor facade. Accepted trade-offs: no SASL (topology = socket perms/polkit/TLS x509/SSH tunnel), upstream API-instability (pin exact version, avoid Deprecated wrappers, use *.gen.go functions). Facade must probe /run/libvirt/virtqemud-sock → /var/run/libvirt/libvirt-sock → ?socket= override.
2. **BUI stack: templ + htmx** (chi v5 router, SSE for live telemetry, coder/websocket only for bidirectional needs like VM console). Single binary via go:embed all:dist + SKIP_WEB.
3. **Remote topology: Hub + Agent** (beszel-proven): WS+CBOR primary transport, no-PTY SSH fallback, shared handler registry. A separate lightweight agent binary EXISTS in the product family. Version negotiation via CBOR envelope field (not SSH banner).
4. **EL8 scope: best-effort** — EL9/10 first-class; EL8 core features work, EL8-specific edges (cgroups v1 sensors, virt:rhel module) gated behind build tags / feature detection. GOAMD64=v1 universal artifact (default; optional v3 EL10 artifact deferred).

These decisions are user-ratified and BINDING for blueprint, personas, rules, and knowledge base.

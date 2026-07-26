# VCS Reconnaissance Report — AutoNix Swarm (2026-07-26, researcher-vcs-github)

## Dimension A — Claude Code Swarm Configuration Exemplars

### A1. wshobson/agents (38.2K★, push 2026-07-22) — /tmp/autonix-research/wshobson-agents
Multi-harness plugin marketplace: `.claude-plugin/marketplace.json` (94 plugins), `plugins/<name>/agents/*.md` + `plugins/<name>/skills/<skill>/SKILL.md` + `references/*.md` progressive disclosure. 203 agents, 175 skills. Their `golang-pro.md` omits `tools:` entirely (inherits all) — LOOSER than AutoNix least-privilege standard, do NOT copy that.
**Steal:** skills-as-reference-libraries pattern (short personas, deep domain refs in separate markdown — e.g. libvirt XML schema notes, EL10 systemd/SELinux specifics); "Use PROACTIVELY for…" description triggers; role bundles (backend-development, cicd-automation); `## Purpose → ## Capabilities` persona layout.

### A2. VoltAgent/awesome-claude-code-subagents (23.7K★, push 2026-07-10) — /tmp/autonix-research/voltagent-subagents
172 agents in numbered categories (01-core-development … 09-meta-orchestration, 10-research-analysis). Its `golang-pro.md` is the **closest schema-compliant exemplar** to AutoNix rule 03: frontmatter exactly `name`, `description` ("Use when building Go applications requiring…"), `tools: Read, Write, Edit, Bash, Glob, Grep`, `model: sonnet`. Body skeleton: role sentence → `When invoked:` numbered startup protocol (query context → review go.mod → analyze patterns → implement) → domain checklist → pattern lists.
**Steal:** frontmatter shape verbatim; `When invoked: 1..4` boot protocol; Go dev checklist (gofmt/golangci-lint, context propagation, error wrapping, table-driven tests+subtests, benchmarks, race-free, doc comments) as go-developer acceptance criteria; category README indexes as delegation map; 03-infrastructure roster as right-sizing reference.

(Rejected: 0xfurai — 9mo stale; derivative forks — low signal.)

## Dimension B — Production Go Exemplars

### B1. digitalocean/go-libvirt (1.1K★, push 2026-06-09) — /tmp/autonix-research/go-libvirt — PRIMARY DOMAIN DEP
`go 1.24.0`, only 3 direct deps, **zero cgo / no libvirt-devel needed** → decisive for single-binary EL distribution. Layout: `socket/` + `socket/dialers/` (unix socket, TCP, TLS, SSH transports behind one interface), `internal/lvgen` (codegen from libvirt .x XDR protocol defs), `internal/go-xdr`, `internal/event` (async lifecycle events), `libvirttest/` (mock libvirt server for hermetic tests). CI spins real libvirtd for integration tests.
**Steal:** pure-Go RPC over cgo (explicitly reject cgo `libvirt-go-module`); dialers transport abstraction → agentless remote-host management; libvirttest mock-hypervisor pattern for CI without KVM host; codegen-from-upstream-protocol for EL8/9/10 libvirt version drift.

### B2. dmacvicar/terraform-provider-libvirt (1.9K★, push 2026-07-25) — /tmp/autonix-research/terraform-provider-libvirt — DOMAIN LOGIC GOLDMINE
Go 1.26. Canonical modern stack: `digitalocean/go-libvirt` + **`libvirt.org/go/libvirtxml`** (official typed structs for domain/network/pool/volume XML — no hand-rolled XML) + `kdomanski/iso9660` (pure-Go cloud-init seed ISOs). Layout: `internal/libvirt/client.go` hypervisor facade (one seam to mock); `internal/provider/` one file per resource with `<resource>_resource.go` + `_test.go` pairing (domain, network, pool, volume, cloudinit_disk, combustion, ignition) + separate test files per lifecycle concern (create/destroy/undefine-flags/schema); docs generated from templates + runnable examples.
**Steal:** libvirtxml typed structs mandatory; pure-Go ISO generation (no genisoimage shell-out); resource-per-file + test-per-lifecycle discipline for test-engineer; hypervisor-facade boundary; generated docs.

### B3. henrygd/beszel (23.8K★, push 2026-07-19) — /tmp/autonix-research/beszel — BUI EXEMPLAR
Go 1.26.3. Hub-and-agent single-binary: hub = web dashboard on PocketBase with `//go:embed all:dist` (React frontend baked in); agent = metrics collector exposing minimal SSH server (gliderlabs/ssh) as transport — no inbound HTTP on monitored hosts. Deps: `shirou/gopsutil/v4`, `coreos/go-systemd/v22`, `spf13/cobra`, `lxzan/gws`, `fxamacker/cbor/v2`, pocketbase + `modernc.org/sqlite` (**pure-Go SQLite, CGO_ENABLED=0 preserved**). `.goreleaser.yml`: both binaries CGO_ENABLED=0, multi-arch, **nfpms block installing systemd unit** with postinstall/prerm/postremove — but emits deb only. Dedicated `vulncheck.yml` CI workflow.
**Steal:** go:embed frontend + SKIP_WEB flag; CGO_ENABLED=0 end-to-end incl. DB; SSH-as-transport agentless pattern; go-systemd/v22 + gopsutil/v4 as vetted EL pair; nfpms packaging blueprint (EXTEND to rpm for EL!); build-tag-gated optional features (NVML auto) for EL8↔EL10 capability drift; standing govulncheck workflow.

### B4. derailed/k9s (34.2K★, push 2026-07-25) — /tmp/autonix-research/k9s — TUI EXEMPLAR
Go 1.25.8. Deliberately NOT Bubble Tea — `derailed/tview` + `tcell/v2` forks for dense table-heavy multi-pane browsers. Layering under `internal/`: `ui/` (widgets), `view/` (screens), `model/` (view models), `render/`, `dao/`, `client/`, `watch/` (live resource watching), `config/`, `tchart/`, `xray/`, `plugins/`, `skins/`. Makefile: CGO_ENABLED=0, netgo tag, SOURCE_DATE_EPOCH reproducible builds, ldflags version/commit/date injection. `.golangci.yml`, separate lint.yml + test.yml.
**Steal:** ui/view/model/render/dao/watch layering as mandated TUI package layout; `watch/` first-class (live VM/service list = libvirt domain-list problem); framework guidance: tview/tcell for dense resource managers, Bubble Tea (44K★, ecosystem default) for wizard/linear flows — tui-developer must justify choice, not default blindly; skins + plugins user extensibility; reproducible-build Makefile.

### B5. glanceapp/glance (36K★, push 2026-05-30) — /tmp/autonix-research/glance — SUPPLEMENTARY
9 direct deps, **no web framework, no JS build step**: `//go:embed static` + `templates`, server-side `html/template`. Widget-per-file (~30), YAML config, `singleflight.go` request coalescing, `diagnose` self-diagnostic subcommand.
**Steal:** zero-JS-toolchain BUI option (legit for air-gapped EL servers — bui-developer should present both this and beszel's React path to architect); singleflight coalescing for repeated libvirt stat polling; diagnose subcommand for field troubleshooting.

## Cross-Cutting Synthesis
- 2026 Go baseline: go 1.26.x; cobra v1.10.2 uncontested CLI standard; gopsutil/v4 standard metrics lib.
- **Single-binary invariant achievable end-to-end**: go-libvirt + modernc.org/sqlite + kdomanski/iso9660 + go:embed + CGO_ENABLED=0 + netgo. No cgo anywhere.
- **Packaging gap**: no exemplar ships RPM; AutoNix must extend nfpms `formats: [rpm, deb]` with EL systemd unit placement + SELinux considerations → task for generated swarm's domain-researcher.
- Agent schema: VoltAgent frontmatter shape + wshobson skills-with-references pattern.

## Cloned Paths (deep-analysis queue, ranked)
```
P1: /tmp/autonix-research/terraform-provider-libvirt, /tmp/autonix-research/go-libvirt
P2: /tmp/autonix-research/beszel, /tmp/autonix-research/k9s
P3: /tmp/autonix-research/voltagent-subagents, /tmp/autonix-research/wshobson-agents
P4: /tmp/autonix-research/glance (fold into beszel worker)
```

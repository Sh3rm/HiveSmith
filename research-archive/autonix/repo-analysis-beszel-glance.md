# Repo Analysis — beszel (BUI primary) + glance (zero-JS comparison)

## beszel: frontend embedding
- `//go:embed all:dist` + `fs.Sub` strip prefix; build-tagged server_production.go (!development) vs server_development.go (proxies to live Vite dev server). SPA catch-all: /static//assets long Cache-Control, everything else → embedded index.html. CSP env var optional.
- SKIP_WEB Makefile flag skips JS toolchain; placeholder `mkdir -p dist && touch dist/index.html` satisfies go:embed's dir-must-exist. ADOPT (EL build hosts may lack node/bun).

## beszel: transport (CORRECTION to earlier survey)
- **WS-primary, SSH-fallback** (not SSH-primary): agent dials hub over WebSocket; gliderlabs/ssh server only starts when outbound WS fails. Dual-transport, shared handlerRegistry so both execute identical logic. ADOPT.
- SSH hardening: **PtyCallback→false (no shells — pure authenticated binary RPC)**, IdleTimeout 70s, restricted KEX/MACs/ciphers, pubkey-only. ADOPT no-PTY.
- Wire: CBOR everywhere (fxamacker/cbor/v2); RequestManager multiplexes request/response pairs by ID over one persistent conn w/ per-request ctx cancellation.
- Heartbeat: explicit state machine (Disconnected/WS/SSH) + 10s WS retry ticker + 70s read deadline refreshed per message + 5s reconnect grace before marking down (weak-pointer goroutine). Version negotiation via SSH banner semver (fragile — AutoNix: versioned CBOR envelope field instead).
- **No SSE anywhere.** Binary WS+CBOR is right for bidirectional command+telemetry; SSE only for pure server→browser log tailing leaf endpoints.

## beszel: go-systemd/v22 usage
- READ-ONLY D-Bus: NewSystemConnectionContext, ListUnitsByPatternsContext (glob), GetUnitTypePropertyContext (ActiveEnterTimestamp/MemoryPeak/MemoryCurrent/CPUUsageNSec), full props for drill-down. `isSystemdAvailable()` presence check first (paths + /proc/1/comm). SKIP_SYSTEMD opt-out.
- `math.MaxUint64` = "property unsupported" sentinel (EL8 cgroups-v1 vs EL9/10 v2 differences).
- Unit MANAGEMENT (start/stop/enable) = different privilege boundary → polkit-gated D-Bus (org.freedesktop.systemd1.Manager.StartUnit), safety-engineer decision.

## beszel: nfpms packaging (deb-only — EL gap closure recipe)
For RPM: nfpm `formats: [rpm]` + `rpm:` sub-block; unit to /usr/lib/systemd/system/ (packager: rpm dst override); `groupadd -r`/`useradd -r -M -s /sbin/nologin` (no adduser on EL); NO debconf — `%config(noreplace)` empty conf + documented manual edit; `%systemd_post`/`%systemd_preun`/`%systemd_postun_with_restart` macro equivalents (or systemctl daemon-reload/enable --now in %post, stop in %preun); `Requires(pre): shadow-utils`, `Requires(post/preun/postun): systemd`.

## beszel: shipped unit hardening review
Present: User=, StateDirectory= (auto-creates /var/lib/<name> w/ perms — ADOPT, satisfies idempotency), ProtectSystem=strict, ProtectHome=read-only, LockPersonality, ProtectClock/Hostname/KernelLogs, RemoveIPC, RestrictSUIDSGID, KeyringMode=private.
MISSING (AutoNix ships stricter): NoNewPrivileges, PrivateTmp, ProtectKernelModules/Tunables, ProtectControlGroups, RestrictNamespaces, RestrictRealtime, SystemCallFilter, CapabilityBoundingSet, MemoryDenyWriteExecute.

## glance: zero-JS patterns
- embed static+templates; runtime CSS @import bundling via regex (their own comment regrets it — AutoNix: resolve CSS at build/go-generate time); MD5-of-embed-FS hash (10 hex) for cache-busting asset URLs without bundler. 
- Template inheritance: every widget template parsed with shared widget-base.html; named `{{block "widget-content"}}` overrides; single shared template.FuncMap (formatting/escapes). Widget-per-file: widget-<name>.go (struct embedding widgetBase, initialize/update/Render) + templates/<name>.html; plain switch factory, no reflection. ADOPT pairing convention.
- Hand-rolled generic Singleflight[T] + TTL cache + stale-on-error (reddit cookie). AutoNix: prefer x/sync/singleflight (battle-tested, panic handling) unless zero-dep constraint — HITL note.
- `diagnose` subcommand: static []diagnosticStep{name, fn}, concurrent w/ 15s per-check timeouts, Markdown-fenced ✓/✗ output for GitHub issues. ADOPT for EL products (probe D-Bus, systemd socket, docker socket, mounts, DNS) — but probe targets must be configurable for air-gapped environments.

## Knowledge-base bullets (bui-developer)
1. go:embed all:dist + fs.Sub + SKIP_WEB placeholder.
2. SPA catch-all serving pattern; long cache on assets.
3. systemd via go-systemd/v22 D-Bus, presence-check first; never shell to systemctl.
4. MaxUint64 = unsupported property sentinel.
5. Unit management = polkit-gated D-Bus, explicit privilege review.
6. RPM via nfpm rpm: block per recipe above.
7. Unit baseline: beszel's set + NoNewPrivileges/ProtectControlGroups/ProtectKernelModules/RestrictNamespaces and stricter.
8. Binary WS+CBOR for bidirectional; SSE only for browser log-tail leaves.
9. No-PTY SSH fallback channel.
10. Widget = one Go file + one template + shared base blocks + shared FuncMap.
11. diagnose subcommand w/ configurable probes.
12. x/sync/singleflight for coalescing expensive shared lookups.

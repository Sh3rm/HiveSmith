# Tech Stack & Deprecation Research Report — AutoNix (2026-07-26, researcher-tech-stack)
⚠ = deprecated/removed/avoid.

## 1. Go Toolchain
- Current stable: **Go 1.26.5** (2026-07-07); supported: 1.26.x/1.25.x/1.24.x; ⚠ ≤1.23 EOL.
- Go 1.26: `new(expr)`; Green Tea GC default (10–40% GC overhead cut); **cgo call overhead −30%** (relevant to CGo libvirt); `slog.NewMultiHandler` (journald+stdout fan-out stdlib-native); `go fix` modernizers.
- `testing/synctest` **stable since 1.25** — correct way to test pollers/watchers/backoffs; kills time.Sleep flakes.
- ⚠ `encoding/json/v2` still experimental (GOEXPERIMENT) — use v1.
- Recommendation: `go.mod` directive **go 1.25**, build with 1.26 toolchain. **CGO_ENABLED=0 default posture** — static binary runs on EL8 (glibc 2.28)/EL9 (2.34)/EL10. CGo → per-EL-major build matrix (the most consequential fork in the stack). `go.work` workspaces for cli/tui/bui/shared monorepo.

## 2. CLI Framework
- **Cobra v1.10.2 (2025-12-04) NOT deprecated — industry standard** (kubectl, gh, podman). RECOMMENDED.
- urfave/cli v3.8.0 viable alt; ⚠ v2 maintenance-only.
- Viper v1: ⚠ **global singleton discouraged upstream** ("may be deprecated in future"); its Logger deprecated in favor of slog. RULE: always `viper.New()` + DI, never package-level `viper.GetString()`.
- Config precedence: flags > env (`AUTONIX_*`) > `/etc/autonix/config.yaml` > defaults.

## 3. TUI — MAJOR CHANGE
- ⚠ **Charm v2 shipped 2026-02-23 with NEW module path: `charm.land/bubbletea/v2`** (also lipgloss/v2, bubbles/v2). Old `github.com/charmbracelet/bubbletea` imports for v2 = non-compiling code.
- v2 breaking changes: `View()` returns `tea.View` struct (not string); `KeyPressMsg`/`KeyReleaseMsg` with `Code`+`Text`; discrete mouse msg types; ⚠ `EnterAltScreen`/`EnableMouseCellMotion` commands gone (set View struct fields); Paste msgs.
- New "Cursed Renderer" (ncurses algorithm) + terminal synchronized output mode 2026 — ~10x rendering, no tearing. Production-proven in Crush.
- `UPGRADE_GUIDE_V2.md` exists in each repo — feed to tui-developer.
- Bubble Tea 40.3K★, 18K+ apps — dominant. tview/tcell maintained but not recommended here (see VCS report for the k9s counterpoint: tview for dense multi-pane).
- ⚠ Open item: Huh v2 status/module path unconfirmed — verify at build time.

## 4. Web/BUI
- `//go:embed` + `http.FS` = settled single-binary pattern.
- **templ (a-h/templ)**: type-safe compile-time templates, 5,481+ importers, active (2026-05-10). Choose over html/template for real dashboards.
- Hypermedia: **htmx default** (lower risk, ecosystem) vs **Datastar** (15KB, SSE-native signals — natural fit for live VM/host telemetry; DatastarUI = Go/templ shadcn port). Genuine HITL decision point.
- Routing: Go 1.22+ stdlib mux has method+wildcard; **chi v5.3.x recommended** for non-trivial (100% net/http compat, middleware suite).
- ⚠ **gorilla/websocket ARCHIVED (2022), panics on concurrent WriteMessage — forbidden.** Use **coder/websocket** (ctx-aware, safe concurrent writes). **Prefer SSE (stdlib http.Flusher) for server→client streams**; WebSocket only for bidirectional (VM serial console/terminal proxy).
- Beszel = closest architectural analogue (hub+agent, PocketBase hub, ~9MB agent). Cockpit is C/JS not a Go reference, but cockpit-machines' data-access pattern relevant (§8).

## 5. EL 8/9/10 Deprecations & Modern Equivalents
| Legacy (FORBIDDEN) | Status | Replacement |
|---|---|---|
| network-scripts / ifup/ifdown | ⚠ REMOVED EL9 | NetworkManager + nmcli |
| ifcfg-* format | ⚠ REMOVED ENTIRELY EL10 | keyfile in /etc/NetworkManager/system-connections/ |
| teamd/libteam | ⚠ removed EL10 | kernel bonding |
| iptables backend | legacy EL10 | nftables (firewalld default) |
| dnf4 | superseded EL10 | **dnf5** (/usr/bin/dnf → dnf5); microdnf obsoleted |
| monolithic libvirtd | ⚠ deprecated EL9/OL10 | modular daemons (virtqemud, virtnetworkd, virtstoraged…) socket-activated |
| virt-manager | ⚠ NOT shipped in RHEL/Rocky 10 | Cockpit + cockpit-machines |
| x86-64-v2 HW, 32-bit | ⚠ removed EL10 | x86-64-v3 baseline |

Consequences:
1. Network config via **NetworkManager D-Bus** (or nmcli shell-out) ONLY; writing ifcfg files = hard fail.
2. dnf4 vs dnf5 abstraction; detect via `/usr/bin/dnf5` presence — CLI mostly-but-not-fully compatible.
3. EL10 x86-64-v3: consider GOAMD64=v3 for EL10-only artifact, v1 universal.
4. **Podman 5 + Quadlets** (⚠ `podman generate systemd` deprecated). Docker not first-class on EL.
5. **bootc/image-mode RHEL 10** shipping (OCI-delivered OS, soft reboot). RULE: never write to /usr; state/config in /etc and /var only.
6. SELinux enforcing+mature on EL10; ship policy or use existing domain; never `setenforce 0`.

## 6. Go Libraries for Linux System Interaction
- ✅ `coreos/go-systemd/v22` (v22.5.x, pub 2026-01-27) — unit mgmt/journal/socket activation; ⚠ non-v22 path legacy. Never parse systemctl output.
- ✅ `godbus/dbus/v5` — universal escape hatch: NetworkManager, firewalld (org.fedoraproject.FirewallD1), libvirt-dbus. Version-stable across EL8/9/10; more robust than parsing CLI text.
- ✅ `shirou/gopsutil/v4` v4.26.5 — no CGo; ⚠ v4 moved sensors out of `host` into `sensors` package.
- ✅ `vishvananda/netlink` (high-level), `mdlayher/netlink` (low-level, stable v1, pub 2026-04-16).
- SELinux: no mature pure-Go policy lib — use `opencontainers/selinux` + shell out to semanage/restorecon. Accepted gap.

## 7. Testing/Linting/CI/RPM
- ⚠ **golangci-lint v2.12.2: v2 config format MANDATORY** — `version: "2"` field required, v1 configs unparseable; `enable-all/disable-all` → `linters.default`; goimports moved to `formatters:` section. v1 .golangci.yml = broken repo.
- goreleaser v2 + **nfpm v2** for RPM/deb (no rpmbuild/fpm). ⚠ RPM dir-ownership rule: own only /etc/autonix, /var/lib/autonix — never OS dirs. `%config(noreplace)` semantics via nfpm config file type.
- testcontainers-go (pub 2026-06-19) with rockylinux 8/9/10 images for install matrix. ⚠ systemd doesn't run in default containers — systemd/D-Bus/libvirt integration tests need privileged containers or real KVM VMs; self-hosted libvirt test harness is the honest answer.

## 8. Virtualization (KVM/QEMU/libvirt) from Go — THE DECISIVE FORK
| Binding | Mechanism | Status | Verdict |
|---|---|---|---|
| `libvirt.org/go/libvirt` | CGo → libvirt.so | Official, maintained, semver | ✅ Recommended primary |
| `libvirt.org/go/libvirtxml` | Pure Go structs | Official | ✅ Recommended (mandatory for XML) |
| `digitalocean/go-libvirt` | Pure Go XDR RPC over socket | ⚠ "API not stable… use at own risk"; vendor it | Conditional (pure-Go agent path) |
| ⚠ `libvirt.org/libvirt-go`, `libvirt-go-xml` | legacy | ⚠ OBSOLETE | Forbidden |

- Official CGo binding: full API coverage (libvirt ≥1.2.0), but needs libvirt-devel + per-EL build matrix; Go 1.26 cut cgo overhead 30%.
- DO pure-Go: static binary, can talk to remote libvirt without local libs (attractive for hub/agent) — but upstream declares API unstable.
- **Third path: libvirt-dbus (`org.libvirt` system bus) via godbus/v5** — pure Go, officially supported; cockpit-machines precedent (uses virsh or libvirt D-Bus API depending on availability).
- **Recommendation: `libvirt.org/go/libvirt` (CGo) + libvirtxml behind an internal `Hypervisor` interface**, swappable to pure-Go for agent binaries. Surface trade-off to user (HITL).
- **Wrap the API, not the CLI** — virsh output is not a stable contract. Exception: `qemu-img` (no Go-native equivalent; shell out with `--output=json`, exec.CommandContext, never sh -c).
- ⚠ Never hand-build domain XML via string templates — libvirtxml structs only.
- ⚠ Never assume `libvirtd.service` exists (deprecated EL9/OL10) — connect via socket (`/var/run/libvirt/virtqemud-sock` or compat `libvirt-sock`), let socket activation work. `systemctl restart libvirtd` = EL10-broken.
- libvirt versions: OL10.0 = 10.10.0, OL10.1 = 11.5.0 — significant drift; feature-detect via `virConnectGetLibVersion`, never assume by EL major.
- **virt-manager gone on EL10 → Cockpit is the only sanctioned GUI → genuine market gap for a Go single-binary KVM BUI. Validates the product thesis.**
- ⚠ Open item: EL8 `virt:rhel` module stream current state unconfirmed — generated swarm's domain-researcher must verify before shipping EL8 support.

## Recommended Stack (summary table)
Go 1.26.5 toolchain / go.mod 1.25 · slog (+NewMultiHandler) · synctest · Cobra v1.10.2 · Viper v1 explicit instance · charm.land/bubbletea/v2 + bubbles/v2 + lipgloss/v2 (+Huh verify) · chi v5.3.x · templ · htmx default (Datastar evaluate for telemetry) · SSE stdlib, coder/websocket for console · go:embed · go-systemd/v22 · godbus/v5 · gopsutil/v4 · vishvananda+mdlayher netlink · opencontainers/selinux+shell · libvirt.org/go/libvirt + libvirtxml behind Hypervisor interface (alt: DO go-libvirt vendored / libvirt-dbus) · qemu-img shell-out JSON · golangci-lint v2.12.2 · goreleaser+nfpm RPM · testcontainers-go.

## Hard Rules to Encode in Generated Swarm's .claude/rules/
1. ⚠ Never write ifcfg-* files — NetworkManager keyfile/D-Bus only (removed EL10).
2. ⚠ Never import github.com/charmbracelet/bubbletea for v2 — path is charm.land/bubbletea/v2.
3. ⚠ Never gorilla/websocket — coder/websocket or SSE.
4. ⚠ Never libvirt.org/libvirt-go(-xml) legacy paths — libvirt.org/go/{libvirt,libvirtxml}.
5. ⚠ Never assume libvirtd.service — socket activation + modular daemons.
6. ⚠ Never emit golangci-lint v1 config — version: "2" required.
7. ⚠ Never parse virsh/systemctl/nmcli output — API/D-Bus/go-systemd.
8. ⚠ Never hand-build domain XML — libvirtxml structs.
9. Never Viper global instance — viper.New() + DI.
10. Never write to /usr (bootc-incompatible) — /etc and /var only.
11. CGO_ENABLED=0 default; CGo only in libvirt-backed module w/ per-EL build matrix.
12. Feature-detect dnf4/dnf5 and libvirt version — never assume by EL major.

## Open Items for generated swarm's domain-researcher
1. Huh v2 module path/status. 2. EL8 virt:rhel module stream state. 3. DO go-libvirt vs libvirt-dbus spike for pure-Go agent. 4. Datastar vs htmx → HITL to user.

(Key sources: go.dev release/go1.26 docs; charm.land/blog/v2; libvirt.org/golang.html; RHEL 9/10 + Rocky 10 + OL10 official docs; Fedora dnf5 change; golangci-lint migration guide; nfpm/goreleaser docs; pkg.go.dev for version evidence.)

# Repo Analysis — digitalocean/go-libvirt (pure-Go libvirt RPC)

## Transport
- `socket.Dialer` interface: `Dial() (net.Conn, error)`; `Router` hands frames to `Libvirt.Route`. Disconnect signaled by closed channel (`Disconnected()`), not error return — good for facade health checks.
- Dialers (socket/dialers/): local unix (default hardcoded `/var/run/libvirt/libvirt-sock`, 15s timeout), remote TCP (16509), TLS (16514; certs /etc/pki/libvirt + ~/.pki/libvirt; **post-handshake reads ONE extra verification byte** — libvirt quirk), SSH (pure-Go x/crypto/ssh tunnel to remote unix socket; agent/key/password auth builder; known_hosts + TOFU option).
- Functional-options pattern for all dialers. ADOPT interface split + options pattern for AutoNix Hypervisor facade.
- **CRITICAL GAP: zero awareness of modular daemons** — no virtqemud/virtnetworkd/socket-path handling anywhere. On EL9/10 must explicitly pass `dialers.WithSocket(...)` or URI `?socket=` with `/run/libvirt/virtqemud-sock` (system) or session socket. Never rely on default path.

## Events
- `internal/event.Stream`: unbounded non-blocking queue (nil-channel select trick), producers never block. RPC register returns CallbackID → Stream keyed by ID → typed Go channel scoped to context; teardown = deregister RPC then Shutdown. ADOPT this exact shape for AutoNix VM lifecycle watcher (TUI/daemon).

## Codegen (lvgen)
- Two-stage: c-for-go on libvirt C headers (consts) + goyacc parser on remote_protocol.x/qemu_protocol.x XDR defs → *.gen.go. Requires `LIBVIRT_SOURCE` env pointing at configured libvirt checkout; manual per-version task, NOT CI-automatable without pinned libvirt tree.
- No runtime protocol negotiation: bindings frozen at gen time; newer-client-vs-older-server → `ErrUnsupported` from server at runtime.

## Mock server (libvirttest)
- `MockLibvirt` implements Dialer itself via `net.Pipe()`; background handler demuxes program/procedure and replies with hand-crafted XDR byte literals; `Fail` flag toggles error paths; auto-patches serial numbers.
- ADOPT: Dialer-shaped mock + net.Pipe + procedure-keyed canned-response table for facade tests. CAVEAT: generate fixture bytes programmatically (encode real structs / capture real traffic to testdata/), never hand-write XDR hex.

## Stability
- README: "API is not considered stable… highly recommend vendoring." 16+ `// Deprecated:` hand-written wrappers (Domains, DomainState, Shutdown, Reboot, New(conn)…) — prefer generated functions (DomainShutdownFlags, ConnectListAllDomains) directly. Pin exact commit/tag.

## Auth
- Connect flow: socket.Connect → watcher goroutine BEFORE auth → AuthList (mandatory even for no-auth) → handles only AuthNone + AuthPolkit. **SASL NOT implemented** — remote setups needing `auth_tcp="sasl"` unsupported; plan topology around local socket perms / polkit / TLS x509 / SSH tunnel.

## Knowledge-base bullets (for AutoNix go developers)
1. Pure-Go XDR RPC over socket — no cgo, no virsh.
2. Default dial path = monolithic libvirtd sock; EL9/10 modular daemons need explicit virtqemud-sock path.
3. URI scheme picks transport: qemu:///system unix; +tcp 16509; +tls 16514 (mTLS certs); +ssh tunnel.
4. TLS dialer must read 1 extra verification byte post-handshake.
5. No SASL; AuthNone + AuthPolkit only; AuthList call mandatory.
6. Events: CallbackID-keyed unbounded stream → context-scoped typed channel; deregister-then-shutdown on teardown.
7. Bindings frozen at codegen; server ErrUnsupported = version skew signal.
8. Regen requires configured libvirt source (LIBVIRT_SOURCE + configure/meson) — manual maintenance task.
9. Vendor/pin exact version; avoid Deprecated wrappers, use *.gen.go functions.
10. Test pattern: Dialer mock + net.Pipe + canned response table; programmatic fixtures, not hand-hex.

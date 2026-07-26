# Repo Analysis — terraform-provider-libvirt (domain-logic goldmine)

**CRITICAL: uses digitalocean/go-libvirt (pure-Go RPC) at runtime, NOT CGo libvirt.org/go/libvirt.** Only libvirtxml for typed XML. No CGo, no libvirt-devel to build. Production evidence FOR the pure-Go path — shifts the HITL trade-off.

## libvirtxml usage
- Thin marshal/unmarshal wrapper per type (internal/libvirt/domain_xml.go, 17 lines, error-wrapped, no logic). ADOPT verbatim pattern for Domain/StorageVolume/StoragePool/Network.
- XML↔model converters are CODE-GENERATED (internal/codegen: reflection over libvirtxml struct tags → IR → template) — not hand-written. ADOPT if exposing many libvirtxml-shaped resources; budget for union/mutually-exclusive field policies. AVOID hand-mapping hundreds of fields.

## Facade & dialers
- NewClient: parse URI (driver[+transport]://…?socket=), dialer factory per transport, single connection per client, caches `ConnectGetLibVersion()` at connect for capability gating. No pooling/retry (GAP — AutoNix adds bounded retry+backoff around Dial/ConnectToURI only; keep wrap-and-surface for permanent errors).
- ⚠ Same modular-daemon gap: hardcodes `/var/run/libvirt/libvirt-sock`; only manual `?socket=` escape. AutoNix MUST probe `/run/libvirt/virtqemud-sock` first, fall back to legacy, keep override.
- SSHCmd dialer: shells out to native `ssh` (respects ~/.ssh/config), ProxyMode auto/native/netcat mirroring libvirt's virt-ssh-helper→nc fallback. ADOPT wholesale for remote-host mgmt. sshCmdConn implements net.Conn over subprocess pipes; ring-buffers last 5 stderr lines for diagnostics.

## Lifecycle discipline
- **Rollback-on-partial-failure**: after DomainDefineXML, capture `cleanupOnError` closure (destroy-if-started + undefine), call from EVERY subsequent failure branch; cleanup errors = warnings, never mask original. Same in pool_resource. ADOPT as canonical pattern (satisfies rule 05).
- **Graceful→forced stop ladder**: DomainShutdown (ACPI) → poll for DomainShutoff w/ bounded timeout → DomainDestroyFlags only on timeout. Update default: 30s+force; Delete default: fail (not force) unless opted in. ADOPT; but add ctx.Done() to poll loop (their waitForDomainState lacks cancellation; waitForInterfaceIP has it).
- **Version-gated flags**: min-version constants (e.g. UndefineNvram ≥1_002_009, UndefineTpm ≥8_009_000) + pure functions deriving flag bits from cached libVersion; fallback to plain call below min. Table-driven boundary tests (8_008_999 vs 8_009_000). ADOPT verbatim for EL8-vs-EL10 libvirt drift.
- **Immutable resources refuse Update** (volumes, seed ISOs): explicit AddError "requires replacement" — honest replace semantics. ADOPT.

## Cloud-init seed ISO (kdomanski/iso9660)
- NewWriter → AddFile user-data/meta-data/[network-config] → WriteTo(file, "cidata") — **volume label MUST be `cidata`** (NoCloud datasource). Deterministic path = sha256(content)[:16]; os.Stat check before regen = idempotent no-op; Delete tolerates IsNotExist.
- ADOPT near-verbatim; but store under /var/lib/autonix/ (configurable), not os.TempDir().

## Test organization (the pyramid to mandate)
1. Pure unit tests on extracted decision functions (flags, options — no libvirt needed; only possible because logic factored into pure functions).
2. Dialer/arg-building tests asserting on buildSSHArgs() []string — no live transport.
3. TestAcc* integration gated by TF_ACC-style env var; URI overridable via LIBVIRT_TEST_URI (default qemu:///system); **sweepers** force-cleanup test-prefixed leftovers; CheckDestroy asserts not just gone-ness but **destroy-flag side effects** (sentinel file preserved vs path deleted).

## Error handling
- Universal `fmt.Errorf("<action>: %w", err)` short-verb wrapping; clean two-layer split (business logic returns error; boundary translates to diagnostics). ADOPT.
- ⚠ GAP: no libvirt error-code mapping — treats ANY lookup error as "already gone" (conflates not-found with transport/auth failure). AutoNix FIX: check VIR_ERR_NO_DOMAIN/NO_STORAGE_VOL/NO_STORAGE_POOL codes before no-op'ing; surface everything else.

## Knowledge-base bullets
1. Pure-Go go-libvirt + libvirtxml = production-proven, no CGo build chain.
2. EL9/10 modular sockets: probe virtqemud-sock → fallback legacy → ?socket= override.
3. URI parse → per-transport dialers behind one Dialer interface.
4. Native-ssh shell-out is legit for remote transport.
5. Cache libVersion; gate flags via min-version constants + pure functions.
6. Graceful→poll→force stop ladder, cancelable.
7. cleanupOnError closure per provisioning flow.
8. Immutable objects reject update.
9. cidata label + exact filenames for NoCloud ISOs; checksum-named idempotent artifacts.
10. Map libvirt error codes; don't no-op on arbitrary lookup errors.
11. Pure-function flag derivation = testability without libvirtd.
12. Three-tier test pyramid + sweepers + side-effect assertions.
13. Consider codegen for XML↔model layers at scale.

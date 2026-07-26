# Repo Analysis — k9s (TUI architecture)

## Layering (internal/)
client (API conn) → dao (Accessor/Nuker registry per resource, generic fallback for unregistered kinds) → watch (informer factory, push cache) → model (poll+diff+listener orchestration; Table) / model1 (PURE data DTOs: Header/Row/RowEvent/DeltaRow — zero UI/client deps) → render (one Renderer per kind: object→Row) → ui (generic tview widgets, zero domain knowledge) → view (controllers composing ui+dao+model+keybindings+dialogs).
Keypress journey: tcell event → app-global KeyActions → focused widget's per-view KeyActions → view cmd → dialog confirm → model.Table.Delete → dao.Nuker → client; result returns via watch events → model refresh → TableDataChanged → QueueUpdateDraw repaint.

## Live refresh
- Hybrid: push-based watch feeding local cache + poll loop re-reading cache (300ms first tick → 2s default; exponential backoff on failure → TableLoadFailed).
- **Double debounce**: (1) CAS `inUpdate` guard drops overlapping refreshes at data layer; (2) `getUpdating` guard coalesces repaints at UI layer; all paints via QueueUpdateDraw (serialized).
- Bubble Tea mapping: Update/View already serialized by Elm loop → second debounce free; but the libvirt poller goroutine feeding tea.Msg still needs the first CAS guard.
- For low-volume libvirt events: prefer pure event-driven push (tea.Msg per lifecycle event) over poll-cache — simpler, lower latency.

## Destructive-op UX
- `Dangerous: true` tag on key actions at registration; `ClearDanger()` bulk-strips in read-only mode — no scattered if-readonly checks. ADOPT.
- Distinct dialog constructors per destructive class: ShowDelete (propagation dropdown + Force checkbox), drain dialog (multi-field), **ShowConfirmAck = type-to-confirm exact string** for highest-risk ops. ADOPT for VM destroy / pool delete (graceful-vs-force dropdown).

## Skins & plugins
- Skins: YAML keyed by widget region + StylesChanged live-reload broadcast → maps to Lip Gloss style structs + tea.Msg on file change.
- Plugins YAML: scopes (view gating), dangerous+confirm, typed inputs[] pre-exec form, env substitution. ⚠ k9s runs plugins via `sh -c` with unsanitized $NAME/INPUT_* substitution = shell-injection surface. AutoNix MUST use exec.Command argv arrays + validation.

## Build & lint
- Makefile: `CGO_ENABLED=0`, `GO_TAGS=netgo`, `-ldflags "-w -s -X cmd.version/-commit/-date"`, SOURCE_DATE_EPOCH reproducible date. ADOPT as template.
- .golangci.yml (v2): sloglint kv-only/no-raw-keys/camel/forbidden-keys enforcing slog discipline; depguard denying logrus/pkg-errors; gocyclo 35, funlen 60. ⚠ Their gosec excludes include G204 (subprocess w/ variable) — do NOT inherit; AutoNix triages G204 individually.

## Performance
- No row virtualization anywhere (tview draws viewport only; bubbles/table also materializes all rows) — thousands-of-rows fleets need explicit pagination/windowing, budget the work.
- Clone-under-RLock before render path (Peek→Clone) — watch goroutine and UI never share mutable slices. Row diffing used for visual delta highlighting, not render skipping. Bounded WorkerPool for fan-out. Refresh-rate clamped to ≥2s floor.

## Knowledge-base bullets (tui-developer, Bubble Tea v2 default)
1. Pure display DTO layer separate from stateful watch/poll model — unit-testable rendering.
2. CAS re-entrancy guard on refresh path (own goroutine feeds tea.Msg).
3. Elm loop already serializes Update/View — don't over-engineer paint debounce.
4. Accessor registry + generic fallback for new resource kinds.
5. Destructive commands as tagged data; bulk-gate for read-only.
6. Per-class confirmation dialogs w/ operation-specific fields (Bubble Tea: small sub-model per dialog).
7. Type-to-confirm for highest-risk ops.
8. YAML skins by widget region + live-reload broadcast.
9. Plugin schema: scopes/dangerous/confirm/typed-inputs; argv exec ONLY, never sh -c.
10. CGO_ENABLED=0 + netgo + -w -s -X ldflags + SOURCE_DATE_EPOCH.
11. No framework virtualizes rows — pagination is explicit work.
12. Clone-under-lock before paint.

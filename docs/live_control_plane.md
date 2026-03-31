# Live Control Plane Upgrade

## Current State (Observed)
- Live visibility is tied to snapshot exports and bundle artifacts.
- The dashboard loads from `dashboard_loader.py`, which merges SQLite snapshots with bundle files under `outputs/`.
- Manager reasoning is surfaced via `manager_runs`, `manager_candidate_audits`, and snapshot JSON.
- GitHub state sync (`github_state.py`) and bundle exports are part of the live path.

## Target State
- One live backend, one canonical database, and a single dashboard reading live projections.
- Manager emits append-only events into `manager_events`.
- Theorem routes are first-class, durable entities in `theorem_routes` and `route_evidence`.
- The dashboard reads from projection tables (`live_manager_timeline`, `route_strength_current`, etc.) and streams via SSE.
- Snapshot/report exports remain for archival only (no longer the live system of record).

## Migration Plan
1. **Phase 1: Audit + Isolation**
   - Live API now defaults to the canonical DB, not bundle exports.
   - Bundles remain for archival export only.
2. **Phase 2: Canonical Event Model**
   - `manager_events`, `theorem_routes`, `route_evidence`, and operator command tables added.
3. **Phase 3: Manager Event Emission**
   - Manager tick emits structured events (route selection, scoring, submissions, results, incidents, operator actions).
4. **Phase 4: Route-First Planning**
   - Route assignment and selection layer built on top of existing frontier signals.
5. **Phase 5: Projection Read Models**
   - Live projection tables built and refreshed deterministically.
6. **Phase 6: Live API**
   - REST + SSE endpoints in `dashboard_routes.py` now serve live state.
7. **Phase 7: Dashboard Upgrade**
   - Dashboard UI renders from live projections and streams timeline updates.
8. **Phase 8: Export Demotion**
   - Exports still produced, but no longer required for live visibility.

## Tradeoffs
- SQLite remains the default live database in dev for simplicity. The schema and event model are Postgres-ready; switching to Postgres requires wiring a DB adapter but no schema changes.
- Projections are rebuilt deterministically from events + DB tables rather than a complex streaming pipeline to keep the system reliable and minimal.
- Operator commands are persisted and evented; execution is applied at manager tick boundaries to keep the manager loop simple and predictable.

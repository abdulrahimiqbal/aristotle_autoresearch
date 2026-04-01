#!/usr/bin/env python3
"""Backfill manager_candidate_audits table from existing manager_events data.

This script populates the manager_candidate_audits table by extracting
candidate scoring data from manager_events (type='candidate.scored').

Usage:
    python scripts/backfill_manager_audits.py --db outputs/erdos_live_async/state.sqlite
"""

import argparse
import json
import sqlite3
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_manager_events(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Get all candidate.scored events from manager_events."""
    cursor = conn.execute(
        """
        SELECT
            event_id,
            sequence_no,
            occurred_at,
            project_id,
            run_id,
            experiment_id,
            route_id,
            event_type,
            source_component,
            visibility,
            payload_json
        FROM manager_events
        WHERE event_type = 'candidate.scored'
        ORDER BY occurred_at ASC, sequence_no ASC
        """
    )
    rows = cursor.fetchall()

    events = []
    for row in rows:
        event = dict(row)
        try:
            event["payload"] = json.loads(row["payload_json"] or "{}")
        except json.JSONDecodeError:
            event["payload"] = {}
        events.append(event)

    return events


def get_experiment_info(conn: sqlite3.Connection, experiment_id: str) -> Optional[Dict[str, Any]]:
    """Get experiment info including conjecture_id."""
    row = conn.execute(
        """
        SELECT experiment_id, conjecture_id, candidate_metadata_json
        FROM experiments
        WHERE experiment_id = ?
        """,
        (experiment_id,),
    ).fetchone()

    if row is None:
        return None

    return {
        "experiment_id": row["experiment_id"],
        "conjecture_id": row["conjecture_id"],
        "candidate_metadata": json.loads(row["candidate_metadata_json"] or "{}"),
    }


def build_selection_rationale(payload: Dict[str, Any], event: Dict[str, Any]) -> str:
    """Build a proper selection rationale from the score breakdown."""
    score_breakdown = payload.get("score_breakdown", {})
    bonuses = score_breakdown.get("bonuses", {})
    penalties = score_breakdown.get("penalties", {})
    score = score_breakdown.get("score", 0)
    selected = payload.get("selected", False)

    # Build strategic reasoning
    reasons = []

    if selected:
        reasons.append("Selected by manager policy")
    else:
        reasons.append("Not selected (lower priority)")

    # Add score info
    reasons.append(f"policy_score={score:.2f}")

    # Add top contributing factors
    top_bonuses = sorted(
        [(k, v) for k, v in bonuses.items() if v > 0],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    if top_bonuses:
        bonus_str = ", ".join([f"{k}={v:.2f}" for k, v in top_bonuses])
        reasons.append(f"top_bonuses: {bonus_str}")

    # Add penalties if significant
    top_penalties = sorted(
        [(k, v) for k, v in penalties.items() if v > 0],
        key=lambda x: x[1],
        reverse=True,
    )[:2]

    if top_penalties:
        penalty_str = ", ".join([f"{k}={v:.2f}" for k, v in top_penalties])
        reasons.append(f"penalties: {penalty_str}")

    return "; ".join(reasons)


def backfill_audits(
    conn: sqlite3.Connection,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Backfill manager_candidate_audits from manager_events."""

    # Get existing audits to avoid duplicates
    existing = conn.execute(
        "SELECT DISTINCT experiment_id FROM manager_candidate_audits"
    ).fetchall()
    existing_ids = {row["experiment_id"] for row in existing}

    print(f"Found {len(existing_ids)} existing audit records")

    # Get all candidate.scored events
    events = get_manager_events(conn)
    print(f"Found {len(events)} candidate.scored events")

    # Group events by run_id
    events_by_run: Dict[str, List[Dict[str, Any]]] = {}
    for event in events:
        run_id = event.get("run_id")
        if run_id:
            events_by_run.setdefault(run_id, []).append(event)

    stats = {
        "total_events": len(events),
        "runs_found": len(events_by_run),
        "audits_created": 0,
        "skipped_existing": 0,
        "errors": 0,
    }

    for run_id, run_events in events_by_run.items():
        # Get project_id from first event
        project_id = run_events[0].get("project_id", "unknown")

        # Sort by sequence_no to determine rank position
        run_events.sort(key=lambda e: e.get("sequence_no", 0))

        for rank, event in enumerate(run_events, start=1):
            experiment_id = event.get("experiment_id")
            if not experiment_id:
                continue

            # Skip if already exists
            if experiment_id in existing_ids:
                stats["skipped_existing"] += 1
                continue

            # Get experiment info
            exp_info = get_experiment_info(conn, experiment_id)
            if exp_info is None:
                print(f"  Warning: Experiment {experiment_id} not found, skipping")
                stats["errors"] += 1
                continue

            payload = event.get("payload", {})
            score_breakdown = payload.get("score_breakdown", {})

            # Build the candidate object from payload and experiment info
            candidate = {
                "experiment_id": experiment_id,
                "conjecture_id": exp_info["conjecture_id"],
                "rationale": exp_info["candidate_metadata"].get("rationale", ""),
                "move": exp_info["candidate_metadata"].get("move", ""),
                "move_family": exp_info["candidate_metadata"].get("move_family", ""),
                "objective": exp_info["candidate_metadata"].get("objective", ""),
                "modification": exp_info["candidate_metadata"].get("modification", {}),
            }

            # Build selection reason
            selection_reason = build_selection_rationale(payload, event)

            # Determine selected status
            selected = payload.get("selected", False)

            if not dry_run:
                # Insert the audit record
                conn.execute(
                    """
                    INSERT INTO manager_candidate_audits(
                        audit_id, run_id, project_id, experiment_id, conjecture_id,
                        rank_position, selected, selection_reason, policy_score,
                        score_breakdown_json, candidate_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        run_id,
                        project_id,
                        experiment_id,
                        exp_info["conjecture_id"],
                        rank,
                        1 if selected else 0,
                        selection_reason,
                        float(score_breakdown.get("score", 0)),
                        json.dumps(score_breakdown),
                        json.dumps(candidate),
                        event.get("occurred_at", "2024-01-01T00:00:00"),
                    ),
                )

            stats["audits_created"] += 1

            if stats["audits_created"] % 10 == 0:
                print(f"  Created {stats['audits_created']} audits so far...")

    if not dry_run:
        conn.commit()
        print(f"\nCommitted {stats['audits_created']} new audit records")
    else:
        print(f"\nDRY RUN: Would have created {stats['audits_created']} audit records")

    return stats


def print_summary(stats: Dict[str, Any]):
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("BACKFILL SUMMARY")
    print("=" * 60)
    print(f"Total candidate.scored events found: {stats['total_events']}")
    print(f"Unique manager runs: {stats['runs_found']}")
    print(f"Audit records created: {stats['audits_created']}")
    print(f"Skipped (already exists): {stats['skipped_existing']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Backfill manager_candidate_audits from manager_events"
    )
    parser.add_argument(
        "--db",
        default="outputs/erdos_live_async/state.sqlite",
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Error: Database not found: {db_path}")
        sys.exit(1)

    print(f"Connecting to database: {db_path}")
    conn = get_db_connection(str(db_path))

    try:
        # Check tables exist
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {row["name"] for row in tables}

        if "manager_events" not in table_names:
            print("Error: manager_events table not found")
            sys.exit(1)

        if "manager_candidate_audits" not in table_names:
            print("Error: manager_candidate_audits table not found")
            sys.exit(1)

        print(f"Tables found: manager_events, manager_candidate_audits")
        print()

        if args.dry_run:
            print("=== DRY RUN MODE (no changes will be made) ===\n")

        stats = backfill_audits(conn, dry_run=args.dry_run)
        print_summary(stats)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from typing import Any, Dict, List

from research_orchestrator.schema_versions import PROMPT_TEMPLATE_VERSION
from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter


def build_project_constitution(charter: ProjectCharter) -> str:
    return f"""
You are the Research Manager for project {charter.project_id}.

Mission:
{charter.overarching_problem}

Prompt template version:
{PROMPT_TEMPLATE_VERSION}

Success criteria:
{chr(10).join(f"- {item}" for item in charter.success_criteria)}

Non-goals:
{chr(10).join(f"- {item}" for item in charter.non_goals)}

Allowed moves:
{chr(10).join(f"- {item}" for item in charter.allowed_moves)}

Hard rules:
- Do not optimize only for proving the original theorem.
- Do not treat one failed proof attempt as evidence of falsity.
- Stay within the target theorem family unless the move explicitly allows transfer.
- Prefer information gain over raw proof probability when choosing the next run.
""".strip()


def build_manager_prompt(
    charter: ProjectCharter,
    state_summary: Dict[str, Any],
    frontier: List[Dict[str, Any]],
) -> str:
    return f"""
{build_project_constitution(charter)}

Current state summary:
{json.dumps(state_summary, indent=2)}

Candidate frontier:
{json.dumps(frontier, indent=2)}

Choose exactly one next experiment.

You must optimize for:
1. information gain
2. recurring lemma discovery, recurring subgoal discovery, and proof-trace discovery
3. assumption sensitivity and boundary-map exploitation

You must avoid:
- duplicate low-value runs
- overfitting to one formalization
- treating search failure as theorem falsity

Move-family reminders:
- `promote_subgoal` and `promote_trace` isolate recurring mathematical bottlenecks
- `boundary_map_from_witness` and `boundary_map_from_missing_assumption` should treat fragile falsifications as local boundary evidence
- strong motifs may justify multiple differentiated candidates if they are producing reusable signal

Return:
- chosen move
- target conjecture
- discovery question being answered
- exact modification
- reason
- expected signal
- stop_or_continue
""".strip()


def build_worker_prompt(
    charter: ProjectCharter,
    conjecture: Conjecture,
    brief: ExperimentBrief,
    recurring_lemmas: List[Dict[str, Any]],
    assumption_sensitivity: List[Dict[str, Any]],
) -> str:
    recurring_lines = "\n".join(
        f"- {item['representative_statement']} (reuse={item['reuse_count']})"
        for item in recurring_lemmas[:10]
    ) or "- none yet"
    sensitivity_lines = "\n".join(
        f"- {item['assumption_name']}: avg_sensitivity={item['avg_sensitivity']}"
        for item in assumption_sensitivity[:10]
    ) or "- none yet"

    return f"""
Project charter:
{build_project_constitution(charter)}

Conjecture:
- id: {conjecture.conjecture_id}
- name: {conjecture.name}
- domain: {conjecture.domain}
- natural language: {conjecture.natural_language}
- assumptions: {', '.join(conjecture.assumptions)}

Current experiment:
- experiment_id: {brief.experiment_id}
- move: {brief.move}
- move family: {brief.move_family or brief.move}
- theorem family: {brief.theorem_family_id or conjecture.theorem_family_id or conjecture.domain}
- objective: {brief.objective}
- expected signal: {brief.expected_signal}
- modification: {json.dumps(brief.modification)}
- rationale: {brief.rationale or 'n/a'}
- discovery question id: {brief.discovery_question_id or 'n/a'}
- discovery question: {brief.discovery_question or 'derive the highest-value verification-shaped discovery question for this move'}

Known recurring lemmas:
{recurring_lines}

Known assumption sensitivity:
{sensitivity_lines}

Required behavior:
- Do not conclude falsity from failure.
- Distinguish structural blockers from search blockers and formalization blockers.
- Do not change unrelated parts of the statement.
- Stay within the theorem family and experiment brief.
- Treat verification as discovery: extract reusable structure even from failed proof attempts.
- Return structured outputs.

Required outputs:
- proof artifact if successful
- generated lemmas
- proved lemmas
- unresolved goals
- suspected missing assumptions
- blocker classification in {{structural, search, formalization, malformed, unknown}}
- concise notes
""".strip()

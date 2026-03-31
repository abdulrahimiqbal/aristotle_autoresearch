"""Aristotle result archive parser.

Handles the structured output from `aristotle result <id> --destination <path>`:
- Extracts Lean files from archives (tar.gz, zip)
- Parses JSON manifest files if present
- Classifies output artifacts by type and mathematical content
- Feeds structured content into the VerificationRecord schema

This replaces the conservative "customize result ingestion" placeholder
in the current AristotleCLIProvider.
"""

from __future__ import annotations

import json
import re
import tarfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from research_orchestrator.lean_parser import (
    LeanDeclaration,
    LeanFileAnalysis,
    LeanProjectAnalysis,
    LeanSorryLocation,
    LeanTacticState,
    parse_lean_errors,
    parse_lean_file,
    parse_lean_project,
)
from research_orchestrator.types import (
    ArtifactProvenance,
    VerificationArtifactKind,
    VerificationObservation,
    VerificationStatus,
)


# ---------------------------------------------------------------------------
# Dataclasses for parsed Aristotle results
# ---------------------------------------------------------------------------

@dataclass
class AristotleManifest:
    """Structured manifest from an Aristotle result archive."""
    project_id: str = ""
    status: str = ""
    sorries_filled: int = 0
    sorries_remaining: int = 0
    theorems_proved: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    lean_version: str = ""
    mathlib_version: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AristotleResultAnalysis:
    """Complete analysis of an Aristotle result archive."""
    archive_path: str = ""
    extract_dir: str = ""
    manifest: Optional[AristotleManifest] = None
    lean_analysis: Optional[LeanProjectAnalysis] = None

    # Structured extractions ready for VerificationRecord
    proved_lemmas: List[VerificationObservation] = field(default_factory=list)
    generated_lemmas: List[VerificationObservation] = field(default_factory=list)
    unsolved_goals: List[VerificationObservation] = field(default_factory=list)
    missing_assumptions: List[VerificationObservation] = field(default_factory=list)
    counterexamples: List[VerificationObservation] = field(default_factory=list)
    blocker_observations: List[VerificationObservation] = field(default_factory=list)
    proof_traces: List[VerificationObservation] = field(default_factory=list)
    artifact_provenance: List[ArtifactProvenance] = field(default_factory=list)

    # Classification
    verification_status: str = VerificationStatus.UNKNOWN.value
    sorry_count: int = 0
    completed_count: int = 0
    error_count: int = 0

    def has_meaningful_content(self) -> bool:
        return bool(
            self.proved_lemmas
            or self.generated_lemmas
            or self.unsolved_goals
            or self.proof_traces
            or self.counterexamples
            or (self.lean_analysis and self.lean_analysis.total_completed_count > 0)
        )


# ---------------------------------------------------------------------------
# Archive extraction
# ---------------------------------------------------------------------------

def _safe_extract_zip(archive_path: Path, dest: Path) -> List[str]:
    """Extract a zip archive safely, rejecting path traversal."""
    root = dest.resolve()
    extracted: List[str] = []
    with zipfile.ZipFile(archive_path) as zf:
        for member in zf.infolist():
            member_path = (dest / member.filename).resolve()
            if not str(member_path).startswith(str(root)):
                continue  # skip unsafe paths
            zf.extract(member, dest)
            if not member.is_dir():
                extracted.append(str(member_path))
    return extracted


def _safe_extract_tar(archive_path: Path, dest: Path) -> List[str]:
    """Extract a tar archive safely, rejecting path traversal."""
    root = dest.resolve()
    extracted: List[str] = []
    with tarfile.open(archive_path) as tf:
        for member in tf.getmembers():
            member_path = (dest / member.name).resolve()
            if not str(member_path).startswith(str(root)):
                continue
            tf.extract(member, dest, filter="data")
            if member.isfile():
                extracted.append(str(member_path))
    return extracted


def extract_archive(archive_path: str) -> Tuple[str, List[str]]:
    """Extract an Aristotle result archive and return (extract_dir, file_list)."""
    path = Path(archive_path)
    if not path.exists():
        return "", []

    extract_dir = path.with_suffix(path.suffix + ".contents")
    if extract_dir.exists():
        # Already extracted
        files = [str(p) for p in extract_dir.rglob("*") if p.is_file()]
        return str(extract_dir), files

    extract_dir.mkdir(parents=True, exist_ok=True)
    try:
        if zipfile.is_zipfile(path):
            files = _safe_extract_zip(path, extract_dir)
        elif tarfile.is_tarfile(path):
            files = _safe_extract_tar(path, extract_dir)
        else:
            # Not an archive - might be a raw Lean file or JSON
            return "", []
    except (tarfile.TarError, zipfile.BadZipFile, OSError):
        return str(extract_dir), []

    return str(extract_dir), files


# ---------------------------------------------------------------------------
# Manifest parsing
# ---------------------------------------------------------------------------

# Known manifest file names that Aristotle might produce
_MANIFEST_NAMES = {
    "manifest.json",
    "result.json",
    "aristotle_result.json",
    "summary.json",
    "output.json",
    "project.json",
}


def _find_manifest(files: List[str]) -> Optional[str]:
    """Find a JSON manifest file in the extracted archive."""
    for path_str in files:
        name = Path(path_str).name.lower()
        if name in _MANIFEST_NAMES:
            return path_str
    # Fallback: any top-level JSON file
    for path_str in files:
        p = Path(path_str)
        if p.suffix.lower() == ".json" and p.stat().st_size < 1_000_000:
            return path_str
    return None


def parse_manifest(manifest_path: str) -> AristotleManifest:
    """Parse an Aristotle JSON manifest file."""
    try:
        text = Path(manifest_path).read_text(encoding="utf-8", errors="ignore")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return AristotleManifest()

    if not isinstance(data, dict):
        return AristotleManifest(raw={"_raw": data})

    return AristotleManifest(
        project_id=str(data.get("project_id", data.get("id", ""))),
        status=str(data.get("status", data.get("result", ""))),
        sorries_filled=int(data.get("sorries_filled", data.get("filled", 0))),
        sorries_remaining=int(data.get("sorries_remaining", data.get("remaining", 0))),
        theorems_proved=[str(t) for t in data.get("theorems_proved", data.get("proved", []))],
        errors=[str(e) for e in data.get("errors", [])],
        lean_version=str(data.get("lean_version", data.get("toolchain", ""))),
        mathlib_version=str(data.get("mathlib_version", "")),
        raw=data,
    )


# ---------------------------------------------------------------------------
# Diff parsing (Aristotle sometimes returns a git diff or before/after)
# ---------------------------------------------------------------------------

_DIFF_ADDED = re.compile(r"^\+\s*(.+)$", re.MULTILINE)
_DIFF_REMOVED = re.compile(r"^-\s*(.+)$", re.MULTILINE)


def _parse_diff_for_changes(diff_text: str) -> Tuple[List[str], List[str]]:
    """Extract added and removed lines from a unified diff."""
    added = [m.group(1) for m in _DIFF_ADDED.finditer(diff_text) if not m.group(1).startswith("++")]
    removed = [m.group(1) for m in _DIFF_REMOVED.finditer(diff_text) if not m.group(1).startswith("--")]
    return added, removed


# ---------------------------------------------------------------------------
# Observation construction
# ---------------------------------------------------------------------------

def _obs(text: str, kind: str, provenance: List[ArtifactProvenance], confidence: float = 0.7) -> VerificationObservation:
    """Create a VerificationObservation with proper artifact kind."""
    return VerificationObservation(
        text=text,
        artifact_kind=kind,
        confidence=confidence,
        provenance=provenance,
    )


def _provenance_for(file_path: str, source: str = "lean") -> ArtifactProvenance:
    return ArtifactProvenance(
        kind="artifact",
        path=file_path,
        source=source,
        confidence=0.9,
    )


# ---------------------------------------------------------------------------
# Main analysis pipeline
# ---------------------------------------------------------------------------

def _classify_from_lean_analysis(
    lean: LeanProjectAnalysis,
    manifest: Optional[AristotleManifest],
) -> str:
    """Classify the verification status from Lean analysis + manifest."""
    # Manifest status takes priority if available
    if manifest and manifest.status:
        status_lower = manifest.status.lower()
        if "complete" in status_lower and manifest.sorries_remaining == 0:
            return VerificationStatus.PROVED.value
        if "complete" in status_lower and manifest.sorries_remaining > 0:
            return VerificationStatus.PARTIAL.value
        if "failed" in status_lower or "error" in status_lower:
            if lean.total_completed_count > 0:
                return VerificationStatus.PARTIAL.value
            return VerificationStatus.STALLED.value

    # Fall back to Lean file analysis
    if lean.total_sorry_count == 0 and lean.total_completed_count > 0:
        return VerificationStatus.PROVED.value
    if lean.total_completed_count > 0 and lean.total_sorry_count > 0:
        return VerificationStatus.PARTIAL.value
    if lean.total_sorry_count > 0 and lean.total_completed_count == 0:
        return VerificationStatus.STALLED.value
    if lean.all_errors:
        timeout_errors = [e for e in lean.all_errors if e.category == "timeout"]
        if timeout_errors:
            return VerificationStatus.STALLED.value
    return VerificationStatus.UNKNOWN.value


def analyze_aristotle_result(
    artifact_paths: List[str],
    stdout: str = "",
    stderr: str = "",
    workspace_dir: str = "",
) -> AristotleResultAnalysis:
    """Analyze Aristotle result artifacts and produce structured observations.

    This is the main entry point. It:
    1. Extracts archives if needed
    2. Parses any JSON manifest
    3. Parses all Lean files
    4. Parses error output for tactic states
    5. Classifies the overall result
    6. Produces VerificationObservation lists ready for the record
    """
    result = AristotleResultAnalysis()
    all_files: List[str] = []
    extract_dirs: List[str] = []

    # Step 1: Collect and extract all artifacts
    for path_str in artifact_paths:
        path = Path(path_str)
        if not path.exists():
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    all_files.append(str(child))
            continue
        all_files.append(path_str)
        # Try to extract archives
        if path.suffix.lower() in {".gz", ".tgz", ".zip", ".tar"} or ".tar." in path.name.lower():
            extract_dir, extracted = extract_archive(path_str)
            if extract_dir:
                extract_dirs.append(extract_dir)
                all_files.extend(extracted)
                result.extract_dir = extract_dir

    # Step 2: Parse manifest
    manifest_path = _find_manifest(all_files)
    if manifest_path:
        result.manifest = parse_manifest(manifest_path)
        result.artifact_provenance.append(_provenance_for(manifest_path, "manifest"))

    # Step 3: Parse Lean files
    lean_files = [f for f in all_files if f.endswith(".lean")]

    # Also check extracted directories and workspace
    lean_dirs = extract_dirs[:]
    if workspace_dir and Path(workspace_dir).exists():
        lean_dirs.append(workspace_dir)

    lean_analyses: List[LeanFileAnalysis] = []
    seen_files: set = set()

    for lean_file in lean_files:
        if lean_file in seen_files:
            continue
        seen_files.add(lean_file)
        analysis = parse_lean_file(lean_file)
        lean_analyses.append(analysis)

    for lean_dir in lean_dirs:
        for lean_path in Path(lean_dir).rglob("*.lean"):
            if str(lean_path) in seen_files:
                continue
            if ".lake" in str(lean_path) or "build" in lean_path.parts:
                continue
            seen_files.add(str(lean_path))
            analysis = parse_lean_file(str(lean_path))
            lean_analyses.append(analysis)

    # Build project analysis
    project = LeanProjectAnalysis(files=lean_analyses)
    for analysis in lean_analyses:
        project.total_sorry_count += analysis.sorry_count
        project.total_completed_count += analysis.completed_count
        project.all_sorry_locations.extend(analysis.sorry_locations)
        project.all_completed_proofs.extend(analysis.completed_proofs)
        project.all_intermediate_results.extend(analysis.intermediate_results)
    result.lean_analysis = project

    # Step 4: Parse error output
    error_text = "\n".join(filter(None, [stdout, stderr]))
    for log_file in all_files:
        if Path(log_file).suffix.lower() in {".log", ".txt"}:
            try:
                error_text += "\n" + Path(log_file).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

    errors, tactic_states = parse_lean_errors(error_text)
    project.all_errors.extend(errors)
    project.all_tactic_states.extend(tactic_states)
    result.error_count = len(errors)

    # Step 5: Build provenance
    for lean_file in lean_files[:10]:
        result.artifact_provenance.append(_provenance_for(lean_file, "lean"))

    # Step 6: Build observations
    provenance = result.artifact_provenance[:5]

    # Proved lemmas: from completed proofs in Lean files
    seen_proved: set = set()
    for decl in project.all_completed_proofs:
        key = f"{decl.name} : {decl.signature}"
        if key in seen_proved:
            continue
        seen_proved.add(key)
        result.proved_lemmas.append(_obs(
            key,
            VerificationArtifactKind.LEMMA.value,
            [_provenance_for(decl.file_path, "lean")],
            confidence=0.92,
        ))

    # Also add manifest-reported proved theorems
    if result.manifest:
        for theorem in result.manifest.theorems_proved:
            if theorem not in seen_proved:
                seen_proved.add(theorem)
                result.proved_lemmas.append(_obs(
                    theorem,
                    VerificationArtifactKind.LEMMA.value,
                    provenance,
                    confidence=0.85,
                ))

    # Generated lemmas: intermediate results (have/suffices)
    seen_generated: set = set()
    for decl in project.all_intermediate_results:
        key = f"{decl.name} : {decl.signature}"
        if key in seen_generated or key in seen_proved:
            continue
        seen_generated.add(key)
        result.generated_lemmas.append(_obs(
            key,
            VerificationArtifactKind.LEMMA.value,
            [_provenance_for(decl.file_path, "lean")],
            confidence=0.75,
        ))

    # Also add declarations with sorries as generated (they show structure)
    for decl in project.all_sorry_locations:
        goal = decl.goal_context.strip()
        if goal and goal not in seen_generated:
            seen_generated.add(goal)
            result.generated_lemmas.append(_obs(
                f"{decl.enclosing_declaration} [sorry at line {decl.line_number}]: {goal[:200]}",
                VerificationArtifactKind.LEMMA.value,
                [_provenance_for(decl.file_path, "lean")],
                confidence=0.6,
            ))

    # Unsolved goals: from tactic states and sorry locations
    seen_goals: set = set()
    for state in project.all_tactic_states:
        for goal in state.goals:
            if goal not in seen_goals:
                seen_goals.add(goal)
                result.unsolved_goals.append(_obs(
                    goal,
                    VerificationArtifactKind.GOAL.value,
                    provenance,
                    confidence=0.85,
                ))

    for sorry in project.all_sorry_locations:
        goal_key = f"{sorry.enclosing_declaration}: {sorry.goal_context[:100]}"
        if goal_key not in seen_goals:
            seen_goals.add(goal_key)
            result.unsolved_goals.append(_obs(
                goal_key,
                VerificationArtifactKind.GOAL.value,
                [_provenance_for(sorry.file_path, "lean")],
                confidence=0.7,
            ))

    # Proof traces: from intermediate results and tactic patterns
    seen_traces: set = set()
    for decl in project.all_intermediate_results:
        trace = f"{decl.kind} {decl.name} : {decl.signature}"
        if trace not in seen_traces:
            seen_traces.add(trace)
            result.proof_traces.append(_obs(
                trace,
                VerificationArtifactKind.PROOF_TRACE.value,
                [_provenance_for(decl.file_path, "lean")],
                confidence=0.7,
            ))

    # Dependencies extracted from proof bodies
    for decl in project.all_completed_proofs + [
        d for f in lean_analyses for d in f.declarations if d.has_sorry
    ]:
        for dep in decl.dependencies[:5]:
            trace = f"depends_on: {dep} (in {decl.name})"
            if trace not in seen_traces:
                seen_traces.add(trace)
                result.proof_traces.append(_obs(
                    trace,
                    VerificationArtifactKind.PROOF_TRACE.value,
                    [_provenance_for(decl.file_path, "lean")],
                    confidence=0.6,
                ))

    # Blocker observations: from errors
    seen_blockers: set = set()
    for error in project.all_errors:
        if error.category in {"sorry", "other"} and error.severity == "info":
            continue
        blocker = f"[{error.category}] {error.message[:200]}"
        if blocker not in seen_blockers:
            seen_blockers.add(blocker)
            result.blocker_observations.append(_obs(
                blocker,
                VerificationArtifactKind.BLOCKER.value,
                [_provenance_for(error.file_path, "lean_error")],
                confidence=0.8,
            ))

    # Step 7: Classify
    result.sorry_count = project.total_sorry_count
    result.completed_count = project.total_completed_count
    result.verification_status = _classify_from_lean_analysis(project, result.manifest)

    return result

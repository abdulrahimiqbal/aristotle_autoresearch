"""Lean 4 source parser for extracting structured mathematical content.

This replaces the regex-based extraction in result_ingestion.py with
a proper multi-pass parser that understands Lean 4 syntax well enough
to extract:

- sorry locations with surrounding goal context
- completed theorem/lemma declarations (no sorry)
- have/suffices intermediate results with their types
- import dependency lists
- tactic state dumps from error output
- namespace/section structure

This is NOT a full Lean parser. It is a best-effort structural extractor
designed for research-orchestrator ingestion. For exact parsing, you would
need to call `lean --run` or use the Lean server protocol.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Dataclasses for parsed Lean content
# ---------------------------------------------------------------------------

@dataclass
class LeanSorryLocation:
    """A sorry found in a Lean file with its surrounding context."""
    file_path: str
    line_number: int
    column: int
    enclosing_declaration: str  # the theorem/lemma/have this sorry belongs to
    enclosing_type: str  # "theorem", "lemma", "have", "suffices", "instance", "def"
    goal_context: str  # the type signature or goal state surrounding the sorry
    namespace: str  # enclosing namespace if any
    sorry_text: str  # the raw line containing sorry


@dataclass
class LeanDeclaration:
    """A theorem, lemma, def, or instance declaration."""
    name: str
    kind: str  # "theorem", "lemma", "def", "instance", "have", "suffices"
    signature: str  # the full type signature
    has_sorry: bool
    has_proof: bool  # has a non-sorry proof body
    line_number: int
    file_path: str
    namespace: str
    body_excerpt: str  # first ~200 chars of the proof body
    dependencies: List[str] = field(default_factory=list)  # names referenced in the body


@dataclass
class LeanTacticState:
    """A tactic state dump from Lean error/info output."""
    goals: List[str]
    hypotheses: List[str]
    source_line: int
    source_file: str
    raw_text: str


@dataclass
class LeanErrorMessage:
    """A structured Lean error or warning."""
    file_path: str
    line_number: int
    column: int
    severity: str  # "error", "warning", "info"
    message: str
    category: str  # "sorry", "type_mismatch", "unknown_identifier", "timeout", "other"


@dataclass
class LeanFileAnalysis:
    """Complete analysis of a single Lean file."""
    file_path: str
    imports: List[str]
    namespaces: List[str]
    declarations: List[LeanDeclaration]
    sorry_locations: List[LeanSorryLocation]
    completed_proofs: List[LeanDeclaration]  # declarations with proofs and no sorry
    intermediate_results: List[LeanDeclaration]  # have/suffices
    errors: List[LeanErrorMessage]
    tactic_states: List[LeanTacticState]
    raw_text: str

    @property
    def has_any_sorry(self) -> bool:
        return bool(self.sorry_locations)

    @property
    def completed_count(self) -> int:
        return len(self.completed_proofs)

    @property
    def sorry_count(self) -> int:
        return len(self.sorry_locations)

    def summary(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "imports": self.imports,
            "namespaces": self.namespaces,
            "declarations": len(self.declarations),
            "sorry_count": self.sorry_count,
            "completed_proofs": self.completed_count,
            "intermediate_results": len(self.intermediate_results),
            "errors": len(self.errors),
            "tactic_states": len(self.tactic_states),
        }


@dataclass
class LeanProjectAnalysis:
    """Analysis of all Lean files in a workspace."""
    files: List[LeanFileAnalysis]
    total_sorry_count: int = 0
    total_completed_count: int = 0
    all_sorry_locations: List[LeanSorryLocation] = field(default_factory=list)
    all_completed_proofs: List[LeanDeclaration] = field(default_factory=list)
    all_intermediate_results: List[LeanDeclaration] = field(default_factory=list)
    all_errors: List[LeanErrorMessage] = field(default_factory=list)
    all_tactic_states: List[LeanTacticState] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Regex patterns for Lean 4 parsing
# ---------------------------------------------------------------------------

# Declaration patterns
_DECL_PATTERN = re.compile(
    r"^\s*(?:(?:noncomputable|private|protected|unsafe)\s+)*"
    r"(?P<kind>theorem|lemma|def|instance|abbrev)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
    r"(?P<rest>.*?)$",
    re.MULTILINE,
)

# Have/suffices patterns (intermediate results)
_INTERMEDIATE_PATTERN = re.compile(
    r"^\s*(?P<kind>have|suffices|let)\s+"
    r"(?:(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)\s*)?:\s*"
    r"(?P<type_sig>.+?)(?:\s*:=|\s*by|\s*from|\s*$)",
    re.MULTILINE,
)

# Sorry pattern
_SORRY_PATTERN = re.compile(r"\bsorry\b")

# Import pattern
_IMPORT_PATTERN = re.compile(r"^\s*import\s+(.+)$", re.MULTILINE)

# Namespace pattern
_NAMESPACE_PATTERN = re.compile(
    r"^\s*(?:namespace|section)\s+([A-Za-z_][A-Za-z0-9_'.]*)",
    re.MULTILINE,
)
_END_NAMESPACE_PATTERN = re.compile(
    r"^\s*end\s+([A-Za-z_][A-Za-z0-9_'.]*)",
    re.MULTILINE,
)

# Tactic state pattern (from Lean error output)
_TACTIC_STATE_PATTERN = re.compile(
    r"(?:unsolved goals|remaining goals|goals?)\s*(?:\(\d+ goals?\))?\s*\n"
    r"((?:.*\n)*?)"
    r"(?=\n\s*\n|\Z)",
    re.IGNORECASE,
)

# Lean error/warning pattern
_LEAN_ERROR_PATTERN = re.compile(
    r"(?P<file>[^\s:]+\.lean):(?P<line>\d+):(?P<col>\d+):\s*"
    r"(?P<severity>error|warning|info):\s*(?P<message>.+?)(?=\n\S|\Z)",
    re.DOTALL,
)

# Goal hypothesis pattern (inside tactic states)
_HYPOTHESIS_PATTERN = re.compile(
    r"^(?P<name>[a-zA-Z_][a-zA-Z0-9_']*)\s*(?:✝\d*)?\s*:\s*(?P<type>.+)$",
    re.MULTILINE,
)
_GOAL_TURNSTILE = re.compile(r"^⊢\s*(?P<goal>.+)$", re.MULTILINE)

# Proof body boundary detection
_PROOF_START = re.compile(r"\s*:=\s*by\b|\s*:=\s*\{|\s*where\b|\s*:=\s*(?!sorry)")
_BY_TACTIC = re.compile(r"\bby\b")


# ---------------------------------------------------------------------------
# Single-file parser
# ---------------------------------------------------------------------------

def _find_declaration_end(text: str, start: int) -> int:
    """Find the approximate end of a declaration body.

    This is a heuristic: we look for the next top-level declaration,
    blank line followed by a declaration keyword, or end of namespace.
    """
    lines = text[start:].split("\n")
    depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0:
            continue
        # Track brace depth
        depth += stripped.count("{") + stripped.count("⟨")
        depth -= stripped.count("}") + stripped.count("⟩")
        depth = max(0, depth)
        # A new top-level declaration at depth 0 ends the current one
        if depth == 0 and _DECL_PATTERN.match(line):
            return start + sum(len(l) + 1 for l in lines[:i])
        # End namespace/section
        if _END_NAMESPACE_PATTERN.match(stripped):
            return start + sum(len(l) + 1 for l in lines[:i])
    return len(text)


def _extract_signature(rest: str, body_text: str) -> str:
    """Extract the type signature from a declaration."""
    # The signature is everything before := or where
    combined = rest
    if ":=" in combined:
        sig = combined.split(":=", 1)[0].strip()
    elif "where" in combined:
        sig = combined.split("where", 1)[0].strip()
    else:
        sig = combined.strip()
    # Also check body_text first line
    if not sig and body_text:
        first_line = body_text.split("\n")[0].strip()
        if ":=" in first_line:
            sig = first_line.split(":=", 1)[0].strip()
    return sig


def _classify_error(message: str) -> str:
    """Classify a Lean error message into a category."""
    lowered = message.lower()
    if "sorry" in lowered:
        return "sorry"
    if "type mismatch" in lowered:
        return "type_mismatch"
    if "unknown identifier" in lowered or "unknown constant" in lowered:
        return "unknown_identifier"
    if "timeout" in lowered or "deterministic timeout" in lowered or "heartbeats" in lowered:
        return "timeout"
    if "maximum recursion" in lowered:
        return "timeout"
    if "declaration uses 'sorry'" in lowered:
        return "sorry"
    return "other"


def _extract_dependencies(body: str) -> List[str]:
    """Extract names referenced in a proof body (best-effort)."""
    # Look for apply/exact/rw/simp references
    deps: List[str] = []
    for pattern in (
        re.compile(r"\b(?:apply|exact|rw|simp\s*\[)\s*([A-Za-z_][A-Za-z0-9_'.]+)"),
        re.compile(r"\b(?:have|let)\s+\w+\s*:=\s*([A-Za-z_][A-Za-z0-9_'.]+)"),
    ):
        for match in pattern.finditer(body):
            name = match.group(1).strip().rstrip(",])")
            if name and name not in deps and name not in ("by", "fun", "with", "do"):
                deps.append(name)
    return deps[:20]


def parse_lean_file(file_path: str, text: Optional[str] = None) -> LeanFileAnalysis:
    """Parse a single Lean 4 file and extract structured content."""
    path = Path(file_path)
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return LeanFileAnalysis(
                file_path=file_path,
                imports=[], namespaces=[], declarations=[],
                sorry_locations=[], completed_proofs=[],
                intermediate_results=[], errors=[],
                tactic_states=[], raw_text="",
            )

    # Extract imports
    imports = [m.group(1).strip() for m in _IMPORT_PATTERN.finditer(text)]

    # Extract namespaces
    namespaces = [m.group(1) for m in _NAMESPACE_PATTERN.finditer(text)]

    # Track current namespace stack
    namespace_stack: List[str] = []
    for line_no, line in enumerate(text.split("\n"), 1):
        ns_match = _NAMESPACE_PATTERN.match(line)
        if ns_match:
            namespace_stack.append(ns_match.group(1))
        end_match = _END_NAMESPACE_PATTERN.match(line.strip())
        if end_match and namespace_stack:
            namespace_stack.pop()

    # Extract declarations
    declarations: List[LeanDeclaration] = []
    sorry_locations: List[LeanSorryLocation] = []
    completed_proofs: List[LeanDeclaration] = []
    intermediate_results: List[LeanDeclaration] = []

    for match in _DECL_PATTERN.finditer(text):
        kind = match.group("kind")
        name = match.group("name")
        rest = match.group("rest")
        line_number = text[:match.start()].count("\n") + 1
        decl_end = _find_declaration_end(text, match.end())
        body_text = text[match.end():decl_end]
        signature = _extract_signature(rest, body_text)
        has_sorry = bool(_SORRY_PATTERN.search(body_text)) or bool(_SORRY_PATTERN.search(rest))
        has_proof = bool(_PROOF_START.search(rest)) or bool(_BY_TACTIC.search(body_text))

        # Determine enclosing namespace
        ns = ""
        ns_stack_at_line: List[str] = []
        for ns_line_no, ns_line in enumerate(text[:match.start()].split("\n"), 1):
            ns_m = _NAMESPACE_PATTERN.match(ns_line)
            if ns_m:
                ns_stack_at_line.append(ns_m.group(1))
            end_m = _END_NAMESPACE_PATTERN.match(ns_line.strip())
            if end_m and ns_stack_at_line:
                ns_stack_at_line.pop()
        ns = ".".join(ns_stack_at_line)

        decl = LeanDeclaration(
            name=name,
            kind=kind,
            signature=signature,
            has_sorry=has_sorry,
            has_proof=has_proof and not has_sorry,
            line_number=line_number,
            file_path=file_path,
            namespace=ns,
            body_excerpt=body_text.strip()[:200],
            dependencies=_extract_dependencies(body_text),
        )
        declarations.append(decl)

        if has_sorry:
            # Find each sorry in this declaration's body
            for sorry_match in _SORRY_PATTERN.finditer(body_text):
                sorry_line = text[:match.end() + sorry_match.start()].count("\n") + 1
                sorry_col = sorry_match.start() - body_text.rfind("\n", 0, sorry_match.start()) - 1
                # Extract surrounding context (a few lines around the sorry)
                body_lines = body_text.split("\n")
                sorry_line_in_body = body_text[:sorry_match.start()].count("\n")
                context_start = max(0, sorry_line_in_body - 2)
                context_end = min(len(body_lines), sorry_line_in_body + 3)
                goal_context = "\n".join(body_lines[context_start:context_end])

                sorry_locations.append(LeanSorryLocation(
                    file_path=file_path,
                    line_number=sorry_line,
                    column=max(0, sorry_col),
                    enclosing_declaration=name,
                    enclosing_type=kind,
                    goal_context=goal_context,
                    namespace=ns,
                    sorry_text=body_lines[sorry_line_in_body].strip() if sorry_line_in_body < len(body_lines) else "sorry",
                ))

        if has_proof and not has_sorry:
            completed_proofs.append(decl)

    # Extract intermediate results (have/suffices)
    for match in _INTERMEDIATE_PATTERN.finditer(text):
        kind = match.group("kind")
        name = match.group("name") or f"anonymous_{kind}"
        type_sig = match.group("type_sig").strip()
        line_number = text[:match.start()].count("\n") + 1

        intermediate_results.append(LeanDeclaration(
            name=name,
            kind=kind,
            signature=type_sig,
            has_sorry=False,
            has_proof=True,
            line_number=line_number,
            file_path=file_path,
            namespace="",
            body_excerpt=type_sig[:200],
        ))

    return LeanFileAnalysis(
        file_path=file_path,
        imports=imports,
        namespaces=namespaces,
        declarations=declarations,
        sorry_locations=sorry_locations,
        completed_proofs=completed_proofs,
        intermediate_results=intermediate_results,
        errors=[],
        tactic_states=[],
        raw_text=text,
    )


def parse_lean_errors(error_text: str, source_file: str = "") -> Tuple[List[LeanErrorMessage], List[LeanTacticState]]:
    """Parse Lean compiler/server error output into structured errors and tactic states."""
    errors: List[LeanErrorMessage] = []
    tactic_states: List[LeanTacticState] = []

    # Extract structured errors
    for match in _LEAN_ERROR_PATTERN.finditer(error_text):
        errors.append(LeanErrorMessage(
            file_path=match.group("file"),
            line_number=int(match.group("line")),
            column=int(match.group("col")),
            severity=match.group("severity"),
            message=match.group("message").strip(),
            category=_classify_error(match.group("message")),
        ))

    # Extract tactic states
    for match in _TACTIC_STATE_PATTERN.finditer(error_text):
        state_text = match.group(1).strip()
        goals = [g.group("goal") for g in _GOAL_TURNSTILE.finditer(state_text)]
        hypotheses = [
            f"{h.group('name')} : {h.group('type')}"
            for h in _HYPOTHESIS_PATTERN.finditer(state_text)
        ]
        tactic_states.append(LeanTacticState(
            goals=goals,
            hypotheses=hypotheses,
            source_line=0,
            source_file=source_file,
            raw_text=state_text,
        ))

    return errors, tactic_states


def parse_lean_project(workspace_dir: str) -> LeanProjectAnalysis:
    """Parse all Lean files in a workspace directory."""
    root = Path(workspace_dir)
    if not root.exists():
        return LeanProjectAnalysis(files=[])

    lean_files = sorted(root.rglob("*.lean"))
    analyses: List[LeanFileAnalysis] = []

    for lean_file in lean_files:
        # Skip build artifacts
        if ".lake" in str(lean_file) or "build" in lean_file.parts:
            continue
        analysis = parse_lean_file(str(lean_file))
        analyses.append(analysis)

    project = LeanProjectAnalysis(files=analyses)
    for analysis in analyses:
        project.total_sorry_count += analysis.sorry_count
        project.total_completed_count += analysis.completed_count
        project.all_sorry_locations.extend(analysis.sorry_locations)
        project.all_completed_proofs.extend(analysis.completed_proofs)
        project.all_intermediate_results.extend(analysis.intermediate_results)
        project.all_errors.extend(analysis.errors)
        project.all_tactic_states.extend(analysis.tactic_states)

    return project

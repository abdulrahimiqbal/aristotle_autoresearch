from __future__ import annotations

import hashlib
import re
from typing import Tuple


_VAR_PATTERN = re.compile(r"\b[a-zA-Z]\d*\b")
_COMMENT_PATTERN = re.compile(r"--.*?$|/-.*?-/", re.DOTALL | re.MULTILINE)
_HEADER_PATTERN = re.compile(r"^\s*(?:theorem|lemma|have|suffices)\s+([A-Za-z0-9_'.]+)\s*:\s*", re.IGNORECASE)
_GOAL_LABEL_PATTERN = re.compile(r"^\s*(?:unsolved\s+goal|goal|required goal|need|show|prove)\s*:?\s*", re.IGNORECASE)


def normalize_lemma(statement: str) -> str:
    """Best-effort normalization for recurring-lemma clustering.

    This is deliberately lightweight. For research use, replace this with
    a Lean-aware normalizer or a parser-backed canonicalizer.
    """
    text = statement.strip().lower()
    text = _COMMENT_PATTERN.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("≤", "<=").replace("≥", ">=")
    text = _VAR_PATTERN.sub("v", text)
    text = re.sub(r"\bv\b\s*:\s*[^,)\]]+", "v", text)
    return text.strip()


def normalize_goal(statement: str) -> str:
    text = statement.strip().lower()
    text = _COMMENT_PATTERN.sub(" ", text)
    text = _GOAL_LABEL_PATTERN.sub("", text)
    text = _HEADER_PATTERN.sub("", text)
    text = re.sub(r"\bat\s+line\s+\d+\b", " ", text)
    text = re.sub(r"\bfile\s+\S+\b", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("≤", "<=").replace("≥", ">=")
    text = _VAR_PATTERN.sub("v", text)
    text = re.sub(r"\bv\b\s*:\s*[^,)\]]+", "v", text)
    return text.strip()


def lemma_fingerprint(statement: str) -> Tuple[str, str]:
    normalized = normalize_lemma(statement)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return normalized, digest


def goal_fingerprint(statement: str) -> Tuple[str, str]:
    normalized = normalize_goal(statement)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return normalized, digest

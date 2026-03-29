from __future__ import annotations

import hashlib
import re
from typing import Tuple


_VAR_PATTERN = re.compile(r"\b[a-zA-Z]\d*\b")


def normalize_lemma(statement: str) -> str:
    """Best-effort normalization for recurring-lemma clustering.

    This is deliberately lightweight. For research use, replace this with
    a Lean-aware normalizer or a parser-backed canonicalizer.
    """
    text = statement.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("≤", "<=").replace("≥", ">=")
    text = _VAR_PATTERN.sub("v", text)
    text = re.sub(r"\bv\b\s*:\s*[^,)\]]+", "v", text)
    return text.strip()


def lemma_fingerprint(statement: str) -> Tuple[str, str]:
    normalized = normalize_lemma(statement)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return normalized, digest

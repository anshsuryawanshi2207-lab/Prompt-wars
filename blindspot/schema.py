"""Robust JSON extraction, schema normalisation and the non-directive guardrail."""
from __future__ import annotations

import json
import re
from typing import Any

SEVERITIES = ("LOW", "MEDIUM", "HIGH")
MAP_TYPES = ("EVIDENCE", "ASSUMPTION", "EMOTION", "VALUE", "UNKNOWN")


# ----------------------------------------------------------------- JSON parsing
def extract_json(text: str) -> dict:
    """Pull the first JSON object out of an LLM reply (handles fences, preambles,
    trailing commas). Raises ValueError if nothing parseable is found."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Empty model response")
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.I).strip()
    start = cleaned.find("{")
    if start == -1:
        raise ValueError("No JSON object found")
    depth, in_str, esc, end = 0, False, False, None
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise ValueError("Unbalanced JSON (response likely truncated)")
    blob = cleaned[start : end + 1]
    for candidate in (blob, re.sub(r",\s*([}\]])", r"\1", blob)):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError("Model returned malformed JSON")


# ---------------------------------------------------------------- normalisation
def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _score(v: Any, default: int = 50) -> int:
    try:
        return max(0, min(100, int(round(float(v)))))
    except (TypeError, ValueError):
        return default


def _enum(v: Any, allowed: tuple, default: str) -> str:
    s = _s(v).upper()
    return s if s in allowed else default


def _objs(value: Any, primary: str, fields: tuple) -> list[dict]:
    if value in (None, "", []):
        return []
    if not isinstance(value, list):
        value = [value]
    out = []
    for item in value:
        if isinstance(item, dict):
            d = {f: _s(item.get(f)) for f in fields}
            if not d[primary]:  # tolerate alternate key names
                d[primary] = next((_s(x) for x in item.values() if isinstance(x, str) and _s(x)), "")
            if d[primary]:
                out.append(d)
        elif isinstance(item, (str, int, float)) and _s(item):
            d = {f: "" for f in fields}
            d[primary] = _s(item)
            out.append(d)
    return out


def _strs(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        value = [value]
    out = []
    for x in value:
        if isinstance(x, dict):
            x = next((v for v in x.values() if isinstance(v, str) and v.strip()), "")
        if _s(x):
            out.append(_s(x))
    return out


def normalize(raw: Any) -> dict:
    """Coerce any model output into the exact shape the UI expects."""
    raw = raw if isinstance(raw, dict) else {}
    spots = _objs(raw.get("blind_spots"), "title",
                  ("title", "severity", "explanation", "why_it_matters", "evidence_needed"))
    for b in spots:
        b["severity"] = _enum(b["severity"], SEVERITIES, "MEDIUM")
    assumptions = _objs(raw.get("hidden_assumptions"), "assumption",
                        ("assumption", "confidence", "why_it_might_be_wrong", "how_to_test_it"))
    for a in assumptions:
        a["confidence"] = _enum(a["confidence"], SEVERITIES, "MEDIUM")
    rmap = _objs(raw.get("reasoning_map"), "claim", ("claim", "type", "note"))
    for r in rmap:
        r["type"] = _enum(r["type"], MAP_TYPES, "UNKNOWN")
    balance = []
    items = raw.get("attention_balance")
    for item in items if isinstance(items, list) else []:
        if isinstance(item, dict) and _s(item.get("factor")):
            balance.append({
                "factor": _s(item.get("factor")),
                "importance": _score(item.get("importance", item.get("importance_stated")), 50),
                "attention": _score(item.get("attention", item.get("attention_given")), 50),
                "note": _s(item.get("note")),
            })

    level = _enum(raw.get("blind_spot_level"), SEVERITIES, "")
    if not level:
        highs = sum(b["severity"] == "HIGH" for b in spots)
        level = "HIGH" if highs >= 2 else "MEDIUM" if (highs or len(spots) >= 3) else "LOW"

    return {
        "decision_summary": _s(raw.get("decision_summary")),
        "reasoning_strength": _score(raw.get("reasoning_strength")),
        "information_coverage": _score(raw.get("information_coverage")),
        "assumption_risk": _score(raw.get("assumption_risk")),
        "blind_spot_level": level,
        "analysis_notes": _s(raw.get("analysis_notes")),
        "blind_spots": spots,
        "hidden_assumptions": assumptions,
        "contradictions": _objs(raw.get("contradictions"), "tension",
                                ("tension", "parts_in_tension", "question_to_resolve")),
        "missing_information": _objs(raw.get("missing_information"), "item", ("item", "why_it_matters")),
        "alternative_perspectives": _objs(raw.get("alternative_perspectives"), "perspective",
                                          ("perspective", "insight")),
        "reflection_questions": _strs(raw.get("reflection_questions")),
        "evidence_to_seek": _objs(raw.get("evidence_to_seek"), "action", ("action", "why")),
        "reasoning_strengths": _objs(raw.get("reasoning_strengths"), "strength", ("strength", "detail")),
        "reasoning_map": rmap,
        "attention_balance": balance,
        "mind_changers": _strs(raw.get("mind_changers")),
    }


# -------------------------------------------------------------------- guardrail
_DIRECTIVE = [
    (r"\byou should (choose|pick|select|go with|take|accept|decline|reject|opt for)\b",
     r"you may want to examine whether to \1"),
    (r"\b(?:you must|you need to) (choose|pick|accept|take|go with|decline)\b",
     r"you may want to consider whether to \1"),
    (r"\bI (?:strongly )?(?:recommend|suggest) (?:that you )?(choose|pick|go with|accept|take)\b",
     r"one thing to examine is whether to \1"),
    (r"\b(?:it is|it's) definitely (better|best|wiser|smarter)\b",
     r"it may be worth examining whether it is \1"),
    (r"\boption ([ab]) is (?:clearly |definitely |obviously )?(better|the better|best|the right|the wrong)\b",
     r"it may be worth testing whether option \1 is \2"),
    (r"\bthe (best|right) (choice|option|decision) is\b", r"one view is that the \1 \2 may be"),
]


def _soften(text: str) -> tuple[str, int]:
    total = 0
    for pat, rep in _DIRECTIVE:
        text, n = re.subn(pat, rep, text, flags=re.I)
        total += n
    return text, total


def apply_guardrails(data: Any) -> tuple[Any, int]:
    """Recursively soften any directive phrasing the model slipped in."""
    if isinstance(data, str):
        return _soften(data)
    if isinstance(data, list):
        out, total = [], 0
        for x in data:
            y, n = apply_guardrails(x)
            out.append(y)
            total += n
        return out, total
    if isinstance(data, dict):
        out, total = {}, 0
        for k, v in data.items():
            y, n = apply_guardrails(v)
            out[k] = y
            total += n
        return out, total
    return data, 0

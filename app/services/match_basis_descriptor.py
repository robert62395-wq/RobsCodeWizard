"""Human-readable explanations of translation map matches (v0.5.1)."""
from __future__ import annotations


def describe(entry):
    """Return a sentence describing why this entry was matched."""
    if not entry:
        return ""
    if entry.get("user_override"):
        return "Manual override by user."
    confidence = str(entry.get("confidence", "unmatched"))
    score = entry.get("score", 0)
    match_basis = entry.get("match_basis", []) or []
    vdt = entry.get("vdt") or {}
    odot = entry.get("odot") or {}
    has_both = bool(vdt) and bool(odot)
    if confidence == "unmatched" or not has_both:
        return "No match found in catalog."
    if confidence == "exact":
        if "description" in match_basis and "type" in match_basis:
            return "Exact match on code and description; types match."
        return "Exact match on code."
    if confidence == "best-guess":
        try:
            score_pct = float(score) * 100 if float(score) <= 1.0 else float(score)
        except (TypeError, ValueError):
            score_pct = 0.0
        parts = []
        if "description" in match_basis:
            parts.append(f"description similarity ({score_pct:.0f}%)")
        if "type" in match_basis:
            parts.append("type matched")
        if not parts:
            parts.append(f"similarity score {score_pct:.0f}%")
        return "Best guess: " + ", ".join(parts) + "."
    if confidence == "manual":
        return "Manual override by user."
    return f"Confidence: {confidence}."


def short_label(entry):
    """Return a short label for use in table cells."""
    if not entry:
        return ""
    if entry.get("user_override"):
        return "Manual override"
    confidence = str(entry.get("confidence", "unmatched"))
    if confidence == "exact":
        return "Exact"
    if confidence == "best-guess":
        try:
            score_pct = float(entry.get("score", 0)) * 100
            return f"Best-guess {score_pct:.0f}%"
        except (TypeError, ValueError):
            return "Best-guess"
    if confidence == "unmatched":
        return "Unmatched"
    return str(confidence).title()

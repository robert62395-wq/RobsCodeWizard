"""Row validation."""
from typing import List


def _build_valid_set_and_grammar(codes_or_codeset):
    grammar = None
    valid = None
    if codes_or_codeset is None:
        return frozenset(), None
    if hasattr(codes_or_codeset, "code_set"):
        valid = codes_or_codeset.code_set
        grammar = codes_or_codeset.linework_grammar
    else:
        valid = {str(c).upper() for c in codes_or_codeset}
    return valid, grammar


def validate_rows(rows, codes_or_codeset):
    valid_set, grammar = _build_valid_set_and_grammar(codes_or_codeset)
    grammar_set = frozenset(c.upper() for c in grammar.all_commands) if grammar else frozenset()

    results = []
    for row in rows:
        issues: List[str] = []
        desc = str(row.get("D", "")).strip()
        if not desc:
            issues.append("Empty description")
        try:
            z = float(row.get("Z", 0) or 0)
        except ValueError:
            z = 0.0
            issues.append("Non-numeric elevation")
        if z == 0.0:
            issues.append("Zero elevation")

        bad_tokens = []
        for token in desc.upper().split():
            if not token:
                continue
            if token in grammar_set:
                continue
            stripped = _strip_suffix(token)
            if stripped in valid_set:
                continue
            bad_tokens.append(token)

        if bad_tokens:
            issues.append(f"Unknown code(s): {','.join(bad_tokens)}")

        results.append({"valid": not bad_tokens and bool(desc), "issues": issues})
    return results


def _strip_suffix(token: str) -> str:
    i = len(token)
    while i > 0 and token[i - 1].isdigit():
        i -= 1
    return token[:i] or token

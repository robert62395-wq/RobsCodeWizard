"""Row validation (v0.4.6.1: check full token before stripped suffix)."""
from typing import List

from app.services.size_bearing import is_size_bearing


def _build_valid_set_and_grammar(codes_or_codeset):
    if codes_or_codeset is None:
        return frozenset(), None
    if hasattr(codes_or_codeset, "code_set"):
        return codes_or_codeset.code_set, codes_or_codeset.linework_grammar
    return {str(c).upper() for c in codes_or_codeset}, None


def _strip_suffix(token):
    i = len(token)
    while i > 0 and token[i - 1].isdigit():
        i -= 1
    return token[:i] or token


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

        main = desc.partition("/")[0].strip() if "/" in desc else desc

        bad_tokens = []
        tokens = main.upper().split()
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if not token:
                i += 1
                continue
            if token in grammar_set:
                i += 1
                continue
            # v0.4.6.1: check full token FIRST, then stripped fallback
            if token in valid_set or _strip_suffix(token) in valid_set:
                if is_size_bearing(token) and i + 1 < len(tokens):
                    next_tok = tokens[i + 1]
                    if next_tok not in grammar_set and next_tok not in valid_set and _strip_suffix(next_tok) not in valid_set:
                        i += 2
                        continue
                i += 1
                continue
            bad_tokens.append(token)
            i += 1

        if bad_tokens:
            issues.append(f"Unknown code(s): {','.join(bad_tokens)}")
        results.append({"valid": not bad_tokens and bool(desc), "issues": issues})
    return results

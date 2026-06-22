"""Smart Suggestion engine."""
import difflib


def _split_suffix(token):
    i = len(token)
    while i > 0 and token[i - 1].isdigit():
        i -= 1
    return token[:i] or token, token[i:]


def _normalize(codes_or_codeset):
    if codes_or_codeset is None:
        return [], None
    if hasattr(codes_or_codeset, "code_set"):
        codes = [c["code"] for c in codes_or_codeset.codes]
        return codes, codes_or_codeset.linework_grammar
    return list(codes_or_codeset), None


def suggest(code, codes_or_codeset, cutoff=0.6):
    valid_codes, _ = _normalize(codes_or_codeset)
    if not code or not valid_codes:
        return None
    base, suffix = _split_suffix(code.upper())
    bases = sorted({_split_suffix(c.upper())[0] for c in valid_codes})
    if base in bases:
        return code
    matches = difflib.get_close_matches(base, bases, n=1, cutoff=cutoff)
    if not matches:
        return None
    return matches[0] + suffix


def build_suggestions(rows, codes_or_codeset, results=None):
    valid_codes, grammar = _normalize(codes_or_codeset)
    valid_set = {c.upper() for c in valid_codes}
    grammar_set = frozenset(c.upper() for c in grammar.all_commands) if grammar else frozenset()

    suggestions = []
    for i, row in enumerate(rows):
        if results is not None and results[i]["valid"]:
            suggestions.append("")
            continue
        desc = str(row.get("D", "")).strip()
        if not desc:
            suggestions.append("")
            continue

        out_tokens = []
        changed = False
        for token in desc.upper().split():
            if token in grammar_set:
                out_tokens.append(token)
                continue
            base, _ = _split_suffix(token)
            if base in valid_set:
                out_tokens.append(token)
                continue
            replacement = suggest(token, valid_codes)
            if replacement and replacement != token:
                out_tokens.append(replacement)
                changed = True
            else:
                out_tokens.append(token)
        suggestions.append(" ".join(out_tokens) if changed else "")
    return suggestions

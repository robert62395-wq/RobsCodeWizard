"""Smart Suggestion engine (v0.4.6: orphans behind '/')."""
import difflib

from app.services.size_bearing import is_size_bearing


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

        # v0.4.6: separate existing '/' tail
        if "/" in desc:
            main, _, existing_tail = desc.partition("/")
            main = main.strip()
            existing_tail = existing_tail.strip()
        else:
            main = desc
            existing_tail = ""

        tokens = main.upper().split()
        kept = []
        orphans = []
        changed = False
        i_tok = 0
        while i_tok < len(tokens):
            token = tokens[i_tok]
            if token in grammar_set:
                kept.append(token)
                i_tok += 1
                continue
            base, _ = _split_suffix(token)
            if base in valid_set:
                kept.append(token)
                # v0.4.6: if size-bearing, absorb the next non-code token as size
                if is_size_bearing(token) and i_tok + 1 < len(tokens):
                    next_tok = tokens[i_tok + 1]
                    if next_tok not in grammar_set and _split_suffix(next_tok)[0] not in valid_set:
                        kept.append(next_tok)
                        i_tok += 2
                        continue
                i_tok += 1
                continue
            # Unknown token: try fuzzy match first
            replacement = suggest(token, valid_codes)
            if replacement and replacement.upper() != token:
                kept.append(replacement)
                changed = True
            else:
                orphans.append(token)
                changed = True
            i_tok += 1

        main_out = " ".join(kept)
        tail_parts = orphans[:]
        if existing_tail:
            tail_parts.append(existing_tail)

        if tail_parts and main_out:
            result = f"{main_out} / {' '.join(tail_parts)}"
        elif tail_parts:
            result = f"/ {' '.join(tail_parts)}"
        else:
            result = main_out

        if changed and result != desc:
            suggestions.append(result)
        elif existing_tail and result != desc:
            suggestions.append(result)
        else:
            suggestions.append("")

    return suggestions

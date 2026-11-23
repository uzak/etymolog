"""Find words that are spelled or sound like a query (used by details.py)."""

import unicodedata
from difflib import SequenceMatcher

# digraphs first (order matters), then one class letter per sound
_DIGRAPHS = (("sch", "s"), ("sh", "s"), ("ch", "k"), ("kh", "k"), ("ph", "f"),
             ("bh", "b"), ("dh", "d"), ("gh", "g"), ("th", "t"), ("x", "ks"))
_CLASSES = {c: k for k, chars in (("P", "pbf"), ("T", "td"), ("K", "kgcq"),
                                  ("S", "sz"), ("N", "mn"), ("R", "lr"),
                                  ("W", "vw"), ("J", "jy"), ("V", "aeiou"))
            for c in chars}


def strip(value):
    """lowercase ascii letters only: 'phósphóros' -> 'phosphoros'"""
    nfkd = unicodedata.normalize("NFKD", value.lower())
    return "".join(c for c in nfkd if "a" <= c <= "z")


def sound_classes(value):
    """coarse sound skeleton: 'bhas' and 'phos' both give 'PVS'"""
    s = strip(value)
    for old, new in _DIGRAPHS:
        s = s.replace(old, new)
    result = ""
    for c in s:
        k = _CLASSES.get(c)         # h and anything unknown is dropped
        if k and not result.endswith(k):
            result += k
    return result


def _ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def similar(query, langs, phonetic=False, cutoff=0.7, limit=10, exclude=()):
    """[(score, Word)], best first, from `langs`; `phonetic` also compares sound skeletons.
    Each word is scored by its best form, after the language's key rules."""
    hits = []
    for lang in langs:
        q_text = lang.fold(query)
        q, q_classes = strip(q_text), sound_classes(q_text)
        for word in lang:
            if word in exclude:
                continue
            best = 0
            for form in word.forms or [word.value]:
                text = lang.fold(form)
                score = _ratio(q, strip(text))
                if phonetic:
                    score = (score + _ratio(q_classes, sound_classes(text))) / 2
                best = max(best, score)
            if best >= cutoff:
                hits.append((best, word))
    hits.sort(key=lambda h: (-h[0], h[1].lang.name, h[1].value))
    return hits[:limit]

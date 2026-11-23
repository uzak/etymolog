"""
Similar-looking and similar-sounding word lookup
"""

from . util import *

import lookup
import model
import parser


def langs(*names):
    return [model.World.lang(n) for n in names]


class TestNormalisation:

    def test_strip(self):
        assert lookup.strip("phósphóros") == "phosphoros"
        assert lookup.strip("Čierny") == "cierny"

    def test_sound_classes(self):
        assert lookup.sound_classes("bhas") == lookup.sound_classes("phos") == "PVS"
        assert lookup.sound_classes("mm") == "N"      # repeats squeezed


class TestSimilar(TestCase):

    def test_same_language_by_spelling(self):
        for w in ("water", "war", "zebra"):
            parser.yacc.parse(f"en:{w}")
        hits = lookup.similar("watr", langs("en"))
        assert [h[1].value for h in hits] == ["water", "war"]

    def test_exclude(self):
        parser.yacc.parse("en:water")
        water = lang("en").get_word("water")
        assert lookup.similar("water", langs("en"), exclude=[water]) == []

    def test_accents_are_ignored(self):
        parser.yacc.parse("sk:Cierny")      # typed as ASCII capital for č
        hits = lookup.similar("cierny", langs("sk"))
        assert [h[1].value for h in hits] == ["čierny"]

    def test_other_languages_need_phonetic(self):
        parser.yacc.parse("gr:phos")
        parser.yacc.parse("sa:bhas")
        assert lookup.similar("bhas", langs("gr"), cutoff=0.6) == []
        hits = lookup.similar("bhas", langs("gr"), phonetic=True, cutoff=0.6)
        assert [h[1].key() for h in hits] == ["gr:phos"]

    def test_ties_ordered_by_language_then_value(self):
        for w in ("t:cat", "t:bat", "a:rat"):
            parser.yacc.parse(w)
        hits = lookup.similar("xat", langs("t", "a"), cutoff=0.6)
        assert [h[1].key() for h in hits] == ["a:rat", "t:bat", "t:cat"]

    def test_limit(self):
        for w in ("ab", "ac", "ad"):
            parser.yacc.parse(w)
        assert len(lookup.similar("a", langs("en"), cutoff=0.1, limit=2)) == 2

    def test_finds_ur_names(self):
        parser.yacc.parse("ur:Ugarit")
        hits = lookup.similar("Ugarat", langs("ur"))
        assert [h[1].key() for h in hits] == ["ur:Ugarit"]

    def test_best_form_counts(self):
        parser.yacc.parse("sa:han/hanti")
        hits = lookup.similar("hanti", langs("sa"))
        assert [h[1].key() for h in hits] == ["sa:han/hanti"]
        assert hits[0][0] == 1.0

    def test_english_to_is_ignored(self):
        parser.yacc.parse("en:to go")
        hits = lookup.similar("go", langs("en"))
        assert [h[1].key() for h in hits] == ["en:to go"]
        assert hits[0][0] == 1.0

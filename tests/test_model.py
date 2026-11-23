# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 20:49

"""
test the parser, obviously
"""

from . util import *

class TestModel(TestCase):

    def test_rel_bidirectionality(self):
        en = lang("en")
        w1 = en.add_word("w1")
        w2 = en.add_word("w2")
        assert model.Equals._add(w1, w2) is model.Equals._add(w2, w1)

    def test_rel_get(self):
        en = lang("en")
        w1 = en.add_word("w1")
        w2 = en.add_word("w2")
        eq = model.Equals._add(w1, w2)
        assert model.Equals.get(w2, w1) is eq
        assert model.Related.get(w1, w2) is None
        assert model.Derived.get(w2, w1) is None
        assert model.Equals._add(w2, w1) is eq
        assert model.Equals.all() == [eq]

    def test_derived_is_directional(self):
        en = lang("en")
        w1 = en.add_word("w1")
        w2 = en.add_word("w2")
        d = model.Derived._add(w1, w2)
        assert model.Derived.get(w1, w2) is d
        assert model.Derived.get(w2, w1) is None

    def test_case_insensitiveness(self):
        en = lang("en")
        upper = en.add_word("W1")
        lower = en.add_word("w1")
        assert upper is lower

    def test_case_insensitive_add(self):
        en = lang("en")
        upper = en.add_word("W1")
        lower = en.add_word("w1")
        assert lower is upper

    def test_union_str(self):
        w1 = lang().add_word("w1")
        w2 = lang().add_word("w2")
        w3 = lang().add_word("w3")
        union = model.Union(w1, w2, w3)
        assert str(union) == "w2+w3"


class TestWordForms(TestCase):
    """`root/form` words are found by any of their forms; stored values stay as written"""

    def keys(self, language, query):
        return [w.key() for w in lang(language).get_words(query)]

    def test_forms(self):
        sa = lang("sa")
        assert sa.add_word("han/hanti").forms == ["han", "hanti"]
        assert sa.add_word("vid/vetti/vindati").forms == ["vid", "vetti", "vindati"]
        assert lang("lat").add_word("ango/.ere").forms == ["ango"]     # `.` ending is no form
        assert sa.add_word("plain").forms == ["plain"]

    def test_found_by_any_form(self):
        lang("sa").add_word("han/hanti")
        for query in ("han", "hanti", "han/hanti"):
            assert self.keys("sa", query) == ["sa:han/hanti"]

    def test_dot_ending_is_not_searchable(self):
        lang("lat").add_word("ango/.ere")
        assert self.keys("lat", "ango") == ["lat:ango/.ere"]
        assert self.keys("lat", "ango/.ere") == ["lat:ango/.ere"]
        assert self.keys("lat", "angere") == []

    def test_homonyms_are_not_merged(self):
        sa = lang("sa")
        for v in ("as", "as/asti", "as/asyati"):
            sa.add_word(v)
        assert len(sa) == 3
        assert self.keys("sa", "as") == ["sa:as", "sa:as/asti", "sa:as/asyati"]
        assert self.keys("sa", "asti") == ["sa:as/asti"]

    def test_number_postfix_still_works(self):
        sa = lang("sa")
        sa.add_word("az1")
        sa.add_word("az2")
        sa.add_word("azan")
        assert self.keys("sa", "az") == ["sa:az1", "sa:az2"]


class TestSearchRules(TestCase):

    def test_english_to_is_ignored_when_searching(self):
        en = lang("en")
        en.add_word("go")
        en.add_word("to go")
        en.add_word("tomato")
        for query in ("go", "to go", "To Go"):
            assert [w.key() for w in en.get_words(query)] == ["en:go", "en:to go"]

    def test_stored_value_is_unchanged(self):
        assert lang("en").add_word("to go").value == "to go"

    def test_rules_are_per_language(self):
        lang("de").add_word("to go")
        assert lang("de").get_words("go") == []
        assert [w.value for w in lang("de").get_words("to go")] == ["to go"]

    def test_sort_key(self):
        en, sa = lang("en"), lang("sa")
        assert en.sort_key(en.add_word("to go")) == "go"
        assert sa.sort_key(sa.add_word("Han/hanti")) == "han"
        assert lang("lat").sort_key(lang("lat").add_word("ango/.ere")) == "ango"

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

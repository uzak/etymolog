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
        assert model.Equals(w1, w2) == model.Equals(w2, w1)

    def test_case_insensitivnes(self):
        en = lang("en")
        upper = en.add_word("W1")
        lower = en.add_word("w1")
        assert upper is lower

    def test_case_insensitive_delete(self):
        en = lang("en")
        upper = en.add_word("W1")
        lower = en.add_word("w1")
        en.concat(upper, lower)
        assert en.get_word("W1 w1").value == "W1 W1"
        assert 1 == len(en)

    def test_case_insensitive_add(self):
        en = lang("en")
        upper = en.add_word("W1")
        lower = en.add_word("w1")
        assert lower is upper

    def test_union_str(self):
        l = lang()
        w1 = l.add_word("w1")
        w2 = l.add_word("w2")
        union = model.Union(w1, w2)
        union.register_composite_word()
        assert str(union) == f"{config.default_lang}:w1+w2"

    def test_union_str_explicit_word(self):
        l = lang()
        w1 = l.add_word("w1")
        w2 = l.add_word("w2")
        w3 = l.add_word("abcd")
        union = model.Union(w1, w2)
        w3.union = union
        assert str(w3) == f"{w3.lang.name}:{w3.value} [w1+w2]"

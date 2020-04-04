# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 20:49

"""
test the parser, obviously
"""

from . util import *

import pytest


class TestModel:

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

    @pytest.fixture(autouse=True)
    def run_around_test(self):
        reset_model()
        yield

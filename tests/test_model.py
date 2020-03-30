# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-03-28 20:49

"""
test the parser, obviously
"""

import model


# aliases
lang = model.World.lang
Languages = model.World.Languages


class TestModel:

    def test_rel_bidirectionality(self):
        en = lang("en")
        w1 = en.word("w1")
        w2 = en.word("w2")
        assert model.Equals(w1, w2) == model.Equals(w2, w1)

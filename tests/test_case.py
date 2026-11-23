"""
Languages are case sensitive by default; `en` and `gr` fold case
"""

from . util import *

import model
import parser


class TestCase_(TestCase):

    def test_default_case_sensitive(self):
        parser.yacc.parse("t:varNa")
        parser.yacc.parse("t:varna")
        assert len(lang("t")) == 2
        assert lang("t").get_word("varna").value == "varna"
        assert lang("t").get_word("VARNA") is None

    def test_en_folds(self):
        parser.yacc.parse("en:Adam")
        parser.yacc.parse("en:adam")
        assert len(lang("en")) == 1
        assert lang("en").get_word("ADAM").value == "Adam"

    def test_get_words_exact(self):
        parser.yacc.parse("t:varNa")
        assert lang("t").get_words("varna") == []
        assert len(lang("t").get_words("varNa")) == 1

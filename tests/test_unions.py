"""
Unions are identified by word and components, not by components alone
"""

from . util import *

import model
import parser


class TestUnionIdentity(TestCase):

    def test_same_components_different_words(self):
        parser.yacc.parse("sa:vid {vi+d}")
        parser.yacc.parse("ie:vid {vi+d}")
        assert len(model.Union.Table) == 2
        assert len(lang("sa").get_word("vid").unions) == 1
        assert len(lang("ie").get_word("vid").unions) == 1

    def test_reassert_is_idempotent(self):
        parser.yacc.parse("t:ab {a+b}")
        parser.yacc.parse("t:ab {a+b}")
        assert len(model.Union.Table) == 1
        assert len(lang("t").get_word("ab").unions) == 1

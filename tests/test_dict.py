"""
dict.py: one ancestor line per derivation
"""

from . util import *

import dict as dictmod
import parser


class TestDict(TestCase):

    def test_multiple_derivations(self, capsys):
        for line in ["t:a -> t:w", "t:b -> t:w", "t:c -> t:b"]:
            parser.yacc.parse(line)
        dictmod.dictionary("t")
        out = capsys.readouterr().out
        assert "* w\n    -> t:a\n    -> t:b -> t:c\n" in out

    def test_single_derivation(self, capsys):
        parser.yacc.parse("t:a -> t:w")
        dictmod.dictionary("t")
        assert "* w\n    -> t:a\n" in capsys.readouterr().out

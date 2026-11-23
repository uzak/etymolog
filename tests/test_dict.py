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

    def test_sorting_uses_first_form_and_language_rules(self, capsys):
        for w in ("en:gold", "en:to go", "en:glow", "en:go"):
            parser.yacc.parse(w)
        dictmod.dictionary("en")
        out = capsys.readouterr().out
        entries = [l[2:] for l in out.splitlines() if l.startswith("* ")]
        assert entries == ["glow", "go", "to go", "gold"]

    def test_slash_word_sorts_by_first_form(self, capsys):
        for w in ("t:b", "t:az/zz", "t:c", "t:aa"):
            parser.yacc.parse(w)
        dictmod.dictionary("t")
        entries = [l[2:] for l in capsys.readouterr().out.splitlines() if l.startswith("* ")]
        assert entries == ["aa", "az/zz", "b", "c"]

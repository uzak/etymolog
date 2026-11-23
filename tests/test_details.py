import subprocess
import sys
from pathlib import Path

import pytest

import details
import parser
from . util import TestCase, lang

ROOT = Path(__file__).resolve().parent.parent


def run_script(script, arg, *flags):
    return subprocess.run([sys.executable, script, *flags, arg],
                          cwd=ROOT, capture_output=True, text=True)


def run_details(arg):
    return run_script("details.py", arg)


@pytest.mark.parametrize("arg", ["a:b:c", ":x", "en:"])
def test_malformed_word_argument(arg):
    r = run_details(arg)
    assert r.returncode == 2
    assert "expected [lang:]word" in r.stderr
    assert "Traceback" not in r.stderr


@pytest.mark.parametrize("script,arg", [("details.py", "zz:x"), ("dict.py", "zz")])
def test_unknown_language(script, arg):
    r = run_script(script, arg)
    assert r.returncode == 2
    assert "unknown language: zz" in r.stderr


class TestUnionDerivations(TestCase):
    def test_shows_derivations_of_union_word(self, capsys):
        parser.yacc.parse("t:ab {a+b}")
        parser.yacc.parse("t:ab -> t:c")
        details.details(lang("t").get_word("a"))
        out = capsys.readouterr().out
        assert "+ t:ab" in out
        assert "-> t:c" in out


class TestSimilarFlags:
    def test_similar(self):
        r = run_script("details.py", "en:watr", "--similar")
        assert r.returncode == 0
        assert "Traceback" not in r.stderr
        assert "similar:" in r.stdout and "en:water" in r.stdout

    def test_suggest_includes_other_languages(self):
        r = run_script("details.py", "sa:bhrAtR", "--suggest")
        assert r.returncode == 0
        assert "gr:phrátEr" in r.stdout

    def test_similar_unknown_language(self):
        r = run_script("details.py", "zz:x", "--similar")
        assert r.returncode == 2


class TestFormLookup:
    def test_second_form_finds_the_word(self):
        r = run_script("details.py", "sa:hanti")
        assert r.returncode == 0
        assert "not found" not in r.stdout
        assert "sa:han/hanti" in r.stdout

    def test_english_to_is_ignored(self):
        r = run_script("details.py", "en:go")
        assert "=> en:to go" in r.stdout
        assert "=> en:go" not in r.stdout       # one word, offered once


class TestStackedComments(TestCase):
    """every comment is printed on its own line below the thing it belongs to"""

    def out(self, word_value, capsys, incl_comments=True, language="t"):
        details.pretty_print(lang(language).get_word(word_value), incl_comments=incl_comments)
        return capsys.readouterr().out

    def test_word_header(self, capsys):
        parser.yacc.parse("t:a [x] [y]")
        assert " => t:a\n    [x]\n    [y]\n" in self.out("a", capsys)

    def test_single_comment_is_stacked_too(self, capsys):
        parser.yacc.parse("t:a = [r] t:b")
        assert "    = t:b\n        [r]\n" in self.out("a", capsys)

    def test_relationship_then_word_comments(self, capsys):
        parser.yacc.parse("t:a = [r1] t:b")
        parser.yacc.parse("t:a = [r2] t:b")
        parser.yacc.parse("t:b [w]")
        assert "    = t:b\n        [r1]\n        [r2]\n        [w]\n" in self.out("a", capsys)

    def test_derivation_comments(self, capsys):
        parser.yacc.parse("t:a -> [why] t:b")
        assert "    -> t:b\n        [why]\n" in self.out("a", capsys)

    def test_ancestor_connector_comments(self, capsys):
        parser.yacc.parse("t:p -> [first] t:a")
        parser.yacc.parse("t:p -> [second] t:a")
        assert "      | [first]\n      | [second]\n" in self.out("a", capsys)

    def test_related_lines_are_indented(self, capsys):
        parser.yacc.parse("t:a ~ t:b")
        parser.yacc.parse("t:a ~ [c] t:c")
        lines = [l for l in self.out("a", capsys).splitlines() if "~" in l]
        assert lines and all(l.startswith("    ~ ") for l in lines)

    def test_no_comments_option_hides_all(self, capsys):
        parser.yacc.parse("t:p -> [c1] t:a [c2]")
        parser.yacc.parse("t:a = [c3] t:b [c4]")
        parser.yacc.parse("t:a ~ [c5] t:c")
        parser.yacc.parse("t:a -> [c6] t:d")
        parser.yacc.parse("t:ab {a+b}")
        parser.yacc.parse("t:a = [c7] t:e")
        for w in ("a", "ab"):
            assert "[" not in self.out(w, capsys, incl_comments=False)

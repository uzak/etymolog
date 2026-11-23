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

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run_script(script, arg):
    return subprocess.run([sys.executable, script, arg],
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

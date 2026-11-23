import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def run_details(arg):
    return subprocess.run([sys.executable, "details.py", arg],
                          cwd=ROOT, capture_output=True, text=True)


@pytest.mark.parametrize("arg", ["a:b:c", ":x", "en:"])
def test_malformed_word_argument(arg):
    r = run_details(arg)
    assert r.returncode == 2
    assert "expected [lang:]word" in r.stderr
    assert "Traceback" not in r.stderr

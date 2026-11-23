# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-05-06 19:44

import os
import subprocess


def _rev_no():
    """Commit count of the checkout containing this file; None if unavailable."""
    try:
        out = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, text=True, check=True).stdout
        return int(out.strip())
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


rev_no = _rev_no()

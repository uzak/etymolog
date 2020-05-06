# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-05-06 19:44

import os

rev_no_cmd = "git rev-list --count HEAD"
rev_no = int(os.popen(rev_no_cmd).read().strip())

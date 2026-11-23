# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-06 21:35

"""
Central logging infrastructure
"""

import logging
import os

log = logging.getLogger(__file__)
log_format = '%(asctime)s %(module)s.%(levelname)s: %(message)s'
_level = getattr(logging, os.environ.get("ETYMOLOG_LOG_LEVEL", "WARNING").upper(), logging.WARNING)
logging.basicConfig(format=log_format, level=_level)

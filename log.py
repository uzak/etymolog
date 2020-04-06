# Author   : Martin Užák <martin.uzak@gmail.com>
# Creation : 2020-04-06 21:35

"""
Central logging infrastructure
"""

import logging

log = logging.getLogger(__file__)
log_format = '%(asctime)s %(module)s.%(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

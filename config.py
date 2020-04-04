import logging

# TODO put somewhere else
log = logging.getLogger(__file__)
log_format = '%(asctime)s %(module)s.%(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

default_lang = "en"

default_source = None
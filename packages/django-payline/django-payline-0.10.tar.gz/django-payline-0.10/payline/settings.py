import logging

from test_settings import *  # noqa


PAYLINE_MERCHANT_ID = '11140893378662'
PAYLINE_KEY = '4D4xAp6yoKdp0H2RhYTc'
PAYLINE_VADNBR = '1234567'


logging.basicConfig(
    level=logging.DEBUG,
    format=" %(levelname)s  [%(asctime)s] %(filename)s: %(message)s",
    datefmt='%d-%b %H:%M:%S')
logging.getLogger('suds').setLevel(logging.CRITICAL)

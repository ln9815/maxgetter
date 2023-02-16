import pytest
import logging,sys

from getmax.util import logging_init

logger = logging.getLogger(__name__)

def test_logging_init():
    logging_init(app='PytestDemo',sendto='mingxiangy@126.com')
    try:
        t  = 1/0
    except Exception as e:
        logger.error(e,exc_info=sys.exc_info())
    assert True
    

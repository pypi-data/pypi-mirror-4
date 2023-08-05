import time
import logging

__author__ = 'Alphan Ulusoy (alphan@bu.edu)'

# Logger configuration
logger = logging.getLogger(__name__)
#logger.addHandler(logging.NullHandler())

class Timer:
    """
    LOMAP timer class.

    Examples:
    ---------
    >>> with lomap.Timer():
    >>>     time.sleep(0.1)
    Operation took 100 ms.

    >>> with lomap.Timer('Taking product'):
    >>>     time.sleep(0.1)
    Taking product took 100 ms.
    """
    def __enter__(self):
        self.start = time.time()
    def __init__(self, op_name=None):
        if op_name is not None:
            self.op_name = op_name
        else:
            self.op_name = "Operation"
    def __exit__(self, *args): 
        logger.info('%s took %0.3f ms.' % (self.op_name, (time.time() - self.start)*1000))

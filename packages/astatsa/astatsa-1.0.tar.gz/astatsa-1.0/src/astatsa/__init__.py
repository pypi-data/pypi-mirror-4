__version__ = '1.0'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .expectation import *
from .expectation_weighted import *
from .mean_variance import *
from .prediction import *

"""
Pycord
~~~~~~
Discord API Wrapper

:copyright: 2021-2022 VincentRPS
:license: MIT, see LICENSE for more details.
"""
__title__: str = 'Pycord'
__author__: str = 'Created by VincentRPS, developed by the Pycord Team.'
__version__: str = '3.0.0'
__license__: str = 'MIT'

# colorama is not type stubbed
import colorama  # type: ignore

colorama.init()

del colorama

from .bot import *
from .rest import *
from .state import *
from .user import *
from .utils import *

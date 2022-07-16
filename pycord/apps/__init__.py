"""
pycord.apps
~~~~~~~~~~~
Represents Applications which interact with the Discord API.
"""

from .gateway import *
from .rest import *

app = GatewayApp | RESTApp

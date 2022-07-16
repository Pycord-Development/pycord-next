# Copyright (c) 2021-2022 VincentRPS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pycord.mixins import AssetMixin
from pycord.state import ConnectionState
from pycord.utils import _validate_image_params

__all__ = (
    'Asset',
)

CDN_URL = 'https://cdn.discordapp.com'


class Asset(AssetMixin):
    """Represents a Discord CDN asset.

    !!! note

        All endpoint URLs that can be used with the asset CDN can be found
        [here](https://discord.com/developers/docs/reference#image-formatting-cdn-endpoints).

    Parameters:
        state: The relevant connection state.
        endpoint: The endpoint URL related to the asset with all fields filled in, except for format and size.
                  The URL must also start with a `/`.
        fmt: The format the image will be in.
        size: The size in pixels the image will be set to (must be between 16 and 4096 and a power of 2).

    Attributes:
        url (str): The asset's underlying CDN URL.
        key (str): The asset's identifying hash key.
        animated (bool): Whether the asset is animated.
    """

    def __init__(
        self,
        state: ConnectionState,
        endpoint: str,
        fmt: str = 'png',
        size: int = 128,
    ):
        self._state = state
        self.key = endpoint.split('/')[-1]
        self.animated = self.key.startswith('a_')

        if 'embed/avatars/' in endpoint:  # this endpoint doesn't accept sizes and only takes .png
            self.fmt, self.size = fmt, size
            self.url = CDN_URL + endpoint + '.png'
        else:
            self.fmt, self.size = _validate_image_params(self.key, fmt, size)
            self.url = CDN_URL + endpoint + f'.{self.fmt}?size={self.size}'

    def __str__(self) -> str:
        return self.url

    def __len__(self) -> int:
        return len(self.url)

    def __repr__(self) -> str:
        return f'<Asset url={self.url.replace(CDN_URL, "")} animated={self.animated} fmt={self.fmt} size={self.size}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Asset) and self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)

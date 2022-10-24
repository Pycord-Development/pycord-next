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

import re

from pycord.mixins import AssetMixin, BaseAssetMixin
from pycord.state import BaseConnectionState
from pycord.utils import _validate_image_params

__all__ = ('Asset',)

CDN_URL = 'https://cdn.discordapp.com'


class BaseAsset(BaseAssetMixin):
    def __init__(
        self,
        state: BaseConnectionState,
        path: str,
        key: str,
        fmt: str = 'png',
        size: int = 128,
    ) -> None:
        pass

    def __str__(self) -> str:
        pass

    def __len__(self) -> int:
        pass

    def __repr__(self) -> str:
        pass

    def __eq__(self, other) -> bool:
        pass

    def __hash__(self) -> int:
        pass

    @classmethod
    def from_url(cls, state: BaseConnectionState, url: str) -> "BaseAsset":
        pass

    @property
    def url(self) -> str:
        pass


class Asset(BaseAsset, AssetMixin):
    """Represents a Discord CDN asset.

    !!! note

        All endpoint URLs that can be used with the asset CDN can be found
        [here](https://discord.com/developers/docs/reference#image-formatting-cdn-endpoints).

    Parameters:
        state: The relevant connection state.
        path: The asset's path, excludes key (hash), format, and size.
              The URL must also start with a `/`.
        key: The key (hash) of the image.
        fmt: The format the image will be in.
        size: The size in pixels the image will be set to (must be between 16 and 4096 and a power of 2).

    Attributes:
        url (str): The asset's underlying CDN URL.
        key (str): The asset's identifying hash key.
        path (str): The asset's path, excludes key (hash), format, and size.
        fmt (str): The asset's format (e.g. png, jpg, gif)
        size (int): The size in pixels of the image.
        animated (bool): Whether the asset is animated.
    """

    def __init__(
        self,
        state: BaseConnectionState,
        path: str,
        key: str,
        fmt: str = 'png',
        size: int = 128,
    ):
        self._state = state
        self.path = path
        self.key = key
        self.animated = key.startswith('a_')

        if path.startswith('/embed/avatars/'):  # this endpoint doesn't accept sizes and only takes .png
            fmt = "png"

        self.fmt, self.size = _validate_image_params(self.key, fmt, size)

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

    @classmethod
    def from_url(cls, state: BaseConnectionState, url: str):
        res = re.search(
            r"https://cdn.discordapp.com(/(?:[a-z/]*|[0-9]{15,19})*/)([a-f0-9]*)\.([a-z]{1,3})(?:\?size=([0-9]{1,4}))?",
            url,
        )

        if not res:
            raise TypeError("invalid asset url given")

        path, key, fmt, size = res.groups()
        if not size:
            size = 128

        return cls(state, path, key, fmt, size)

    @property
    def url(self):
        url = f"{CDN_URL}{self.path}{self.key}.{self.fmt}"
        if self.size:
            url += f"?size={self.size}"
        return url

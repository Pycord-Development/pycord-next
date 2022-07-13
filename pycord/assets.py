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


class Asset(AssetMixin):
    CDN_URL = 'https://cdn.discordapp.com'

    def __init__(self, state: ConnectionState, *, url: str, key: str, animated: bool = False):
        self._state = state
        self.url = url
        self.key = key
        self.animated = animated

    def __str__(self) -> str:
        return self.url

    def __len__(self) -> int:
        return len(self.url)

    def __repr__(self) -> str:
        return f'<Asset url={self.url.replace(self.CDN_URL, "")} animated={self.animated}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Asset) and self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)

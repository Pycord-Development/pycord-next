# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
# Copyright (c) 2022-present Pycord Development
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
# SOFTWARE


class Color:
    """Represents the default discord colors.
    Defines factory methods which return a certain color code to be used.
    """

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError('Expected a integer.')

        self.value: int = value

    @classmethod
    def default(cls) -> "Color":
        """A factory color method which returns `0`"""
        return cls(0)

    @classmethod
    def teal(cls) -> "Color":
        """A factory color method which returns `0x1ABC9C`"""
        return cls(0x1ABC9C)

    @classmethod
    def dark_teal(cls) -> "Color":
        """A factory color method which returns `0x11806A`"""
        return cls(0x11806A)

    @classmethod
    def brand_green(cls) -> "Color":
        """A factory color method which returns `0x57F287`"""
        return cls(0x57F287)

    @classmethod
    def green(cls) -> "Color":
        """A factory color method which returns `0x2ECC71`"""
        return cls(0x2ECC71)

    @classmethod
    def dark_green(cls) -> "Color":
        """A factory color method which returns `0x1F8B4C`"""
        return cls(0x1F8B4C)

    @classmethod
    def blue(cls) -> "Color":
        """A factory color method which returns `0x3498DB`"""
        return cls(0x3498DB)

    @classmethod
    def dark_blue(cls) -> "Color":
        """A factory color method which returns `0x206694`"""
        return cls(0x206694)

    @classmethod
    def purple(cls) -> "Color":
        """A factory color method which returns `0x9b59b6`"""
        return cls(0x9B59B6)

    @classmethod
    def dark_purple(cls) -> "Color":
        """A factory color method which returns `0x71368A`"""
        return cls(0x71368A)

    @classmethod
    def magenta(cls) -> "Color":
        """A factory color method which returns `0xE91E63`"""
        return cls(0xE91E63)

    @classmethod
    def dark_magenta(cls) -> "Color":
        """A factory color method which returns `0xAD1457`"""
        return cls(0xAD1457)

    @classmethod
    def gold(cls) -> "Color":
        """A factory color method which returns `0xF1C40F`"""
        return cls(0xF1C40F)

    @classmethod
    def dark_gold(cls) -> "Color":
        """A factory color method which returns `0xC27C0E`"""
        return cls(0xC27C0E)

    @classmethod
    def orange(cls) -> "Color":
        """A factory color method which returns `0xE67E22`"""
        return cls(0xE67E22)

    @classmethod
    def dark_orange(cls) -> "Color":
        """A factory color method which returns `0xA84300`"""
        return cls(0xA84300)

    @classmethod
    def brand_red(cls) -> "Color":
        """A factory color method which returns `0xED4245`"""
        return cls(0xED4245)

    @classmethod
    def red(cls) -> "Color":
        """A factory color method which returns `0xE74C3C`"""
        return cls(0xE74C3C)

    @classmethod
    def dark_red(cls) -> "Color":
        """A factory color method which returns `0x992D22`"""
        return cls(0x992D22)

    @classmethod
    def dark_gray(cls) -> "Color":
        """A factory color method which returns `0x607D8B`"""
        return cls(0x607D8B)

    @classmethod
    def light_gray(cls) -> "Color":
        """A factory color method which returns `0x979C9F`"""
        return cls(0x979C9F)

    @classmethod
    def blurple(cls) -> "Color":
        """A factory color method which returns `0x5865F2`"""
        return cls(0x5865F2)

    @classmethod
    def dark_theme(cls) -> "Color":
        """A factory color method which returns `0x2F3136`"""
        return cls(0x2F3136)

    @classmethod
    def fushia(cls) -> "Color":
        """A factory color method which returns `0xEB459E`"""
        return cls(0xEB459E)

    @classmethod
    def yellow(cls) -> "Color":
        """A factory color method which returns `0xFEE75C`"""
        return cls(0xFEE75C)

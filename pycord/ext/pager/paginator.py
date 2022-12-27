# cython: language_level=3
# Copyright (c) 2021-present Pycord Development
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

from typing import Protocol, TypeVar

from .errors import NoMorePages, PagerException

T = TypeVar('T', covariant=True)


__all__ = ['Page', 'Paginator']


class Page(Protocol[T]):
    """
    The class for all Page Types to subclass.
    """

    def __init__(self):
        ...

    async def interact_forward(self, *args, **kwargs) -> None:
        """
        Interactions to do when the paginator issues a forwarded statement
        """
        ...

    async def interact_backward(self, *args, **kwargs) -> None:
        """
        Interactions to do when the paginator issues a backward statement
        """
        ...


class Paginator:
    """
    Class for paginating between pages.

    Parameters
    ----------
    pages: list[:class:`.Page`]
        Predefined pages
    """

    def __init__(self, pages: list[Page] = []) -> None:
        self._pages = pages
        self._previous_page: tuple[int, Page] | None = None

    def __next__(self) -> Page:
        if self._previous_page is None:
            try:
                page = self._pages[0]
            except IndexError:
                raise PagerException('No pages in paginator')

            self._previous_page = (0, page)

            return page

        new = self._previous_page[0] + 1

        try:
            page = self._pages[new]
        except IndexError:
            raise NoMorePages('No more pages left in the paginator')

        self._previous_page = (new, page)

        return page

    async def forward(self, *args, **kwargs) -> Page:
        """
        Go forward through pages.

        Parameters
        ----------
        args/kwargs:
            Arguments and Keyword-Arguments to put into page.interact_forward.
        """
        page = next(self)

        await page.interact_forward(*args, **kwargs)
        return page

    async def backward(self, *args, **kwargs) -> Page:
        """
        Go backwards from the paginator.
        Only works if the page is not the first page.

        Parameters
        ----------
        args/kwargs:
            Arguments and Keyword-Arguments to put into page.interact_backward.
        """
        if self._previous_page is None or self._previous_page[0] == 0:
            raise PagerException('Unable to go backwards without available pages')

        page = self._pages[self._previous_page[0] - 1]
        self._previous_page = (
            None
            if (self._previous_page[0] - 1) <= 0
            else (self._previous_page[0] - 1, self._pages[self._previous_page[0] - 1])
        )

        await page.interact_backward(*args, **kwargs)
        return page

    @property
    def previous(self) -> Page | None:
        """
        The Previous page of this Paginator
        """
        return None if self._previous_page is None else self._previous_page[1]

    def add_page(self, page: Page) -> None:
        """
        Appends a new page to this Paginator

        Parameters
        ----------
        page: :class:`.Page`
            The page to append
        """
        if page in self._pages:
            raise PagerException('This page has already been added to this paginator')
        self._pages.append(page)

    def remove_page(self, page: Page) -> None:
        """
        Removes a page from this paginator

        Parameters
        ----------
        page: :class:`.Page`
            The page to remove
        """
        if page not in self._pages:
            raise PagerException('This page is not part of this paginator')
        self._pages.remove(page)

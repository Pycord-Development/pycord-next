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
from __future__ import annotations

from .enums import ApplicationRoleConnectionMetadataType
from .types import ApplicationRoleConnectionMetadata as DiscordApplicationRoleConnectionMetadata
from .undefined import UNDEFINED, UndefinedType
from .user import LOCALE

__all__ = (
    'ApplicationRoleConnectionMetadata',
)


class ApplicationRoleConnectionMetadata:
    """Represents a Discord Application's Role Connection Metadata.
    
    Attributes
    ----------
    type: :class:`ApplicationRoleConnectionMetadataType`
        The type of the role connection metadata.
    key: :class:`str`
        The key for the role connection metadata field.
    name: :class:`str`
        The name of the role connection metadata field.
    description: :class:`str`
        The description of the role connection metadata field.
    name_localizations: :class:`dict[str, str]`
        The localizations for the name of the role connection metadata field.
    description_localizations: :class:`dict[str, str]`
        The localizations for the description of the role connection metadata field.
    """

    def __init__(
        self,
        *,
        type: ApplicationRoleConnectionMetadataType,
        key: str,
        name: str,
        description: str,
        name_localizations: dict[LOCALE, str] | UndefinedType = UNDEFINED,
        description_localizations: dict[LOCALE, str] | UndefinedType = UNDEFINED,
    ) -> None:
        self.type: ApplicationRoleConnectionMetadataType = type
        self.key: str = key
        self.name: str = name
        self.description: str = description
        self.name_localizations: dict[LOCALE, str] = name_localizations
        self.description_localizations: dict[LOCALE, str] = description_localizations

    def __repr__(self) -> str:
        return (
            f'<ApplicationRoleConnectionMetadata type={self.type!r} key={self.key!r} name={self.name!r} '
            f'description={self.description!r} name_localizations={self.name_localizations!r} '
            f'description_localizations={self.description_localizations!r}>'
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ApplicationRoleConnectionMetadata:
        type = ApplicationRoleConnectionMetadataType(data.pop('type'))
        return cls(type=type, **data)

    def to_dict(self) -> DiscordApplicationRoleConnectionMetadata:
        return {
            'type': self.type.value,
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'name_localizations': self.name_localizations,
            'description_localizations': self.description_localizations,
        }

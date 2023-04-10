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

import re
from typing import TYPE_CHECKING, Any

from .enums import StickerFormatType, StickerType
from .role import Role
from .snowflake import Snowflake
from .types import (
    Attachment as DiscordAttachment,
    Emoji as DiscordEmoji,
    Sticker as DiscordSticker,
    StickerItem as DiscordStickerItem,
    User as DiscordUser,
)
from .missing import MISSING, MissingEnum, Maybe
from .user import User

if TYPE_CHECKING:
    from .state import State


class Emoji:
    _EMOJI_NAME_REGEX = re.compile(
        r'<?(?P<animated>a)?:?(?P<name>\w+):(?P<id>[0-9]{13,20})>?'
    )

    def __init__(self, data: DiscordEmoji, state: State) -> None:
        self._state: State = state
        self.id: Snowflake | None = (
            Snowflake(data['id']) if data['id'] is not None else None
        )
        self.name: str | None = data.get('name')
        self._roles: list[Snowflake] = [
            Snowflake(role) for role in data.get('roles', [])
        ]
        self.roles: list[Role] = []
        self._user: DiscordUser | MissingEnum = data.get('user', MISSING)
        self.user: MissingEnum | User = (
            User(self._user, state) if self._user is not MISSING else MISSING
        )
        self.require_colons: MissingEnum | bool = data.get(
            'require_colons', MISSING
        )
        self.managed: MissingEnum | bool = data.get('managed', MISSING)
        self.animated: MissingEnum | bool = data.get('animated', MISSING)
        self.available: MissingEnum | bool = data.get('available', MISSING)

    def _inject_roles(self, roles: list[Role]) -> None:
        for role in roles:
            if role.id in self._roles:
                self.roles.append(role)

    def _partial(self) -> dict[str, Any]:
        return {'name': self.name, 'id': self.id, 'animated': self.animated}

    @classmethod
    def _from_str(cls, string: str, state: State) -> 'Emoji':
        match = cls._EMOJI_NAME_REGEX.match(string)

        if match:
            grps = match.groupdict()
            return cls(
                {
                    'animated': bool(grps['animated']),
                    'id': Snowflake(grps['id']),
                    'name': grps['name'],
                },
                state,
            )

        # assumes this is unicode
        return cls({'name': string, 'id': None, 'animated': False}, state)


class StickerItem:
    def __init__(self, data: DiscordStickerItem) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.name: str = data['name']
        self.format_type: StickerFormatType = StickerFormatType(data['format_type'])


class Sticker:
    def __init__(self, data: DiscordSticker, state: State) -> None:
        self.id: Snowflake | None = Snowflake(data['id'])
        self.pack_id: Snowflake | None = (
            Snowflake(data.get('pack_id')) if data.get('pack_id') is not None else None
        )
        self.name: str = data['name']
        self.description: str | None = data['description']
        self.tags: list[str] = data['tags'].split(',')
        self.type: StickerType = StickerType(data['type'])
        self.format_type: StickerFormatType = StickerFormatType(data['format_type'])
        self.available: bool | MissingEnum = data.get('available', MISSING)
        self.guild_id: Snowflake | None = (
            Snowflake(data['guild_id']) if data['guild_id'] is not None else None
        )
        self._user: DiscordUser | MissingEnum = data.get('user', MISSING)
        self.user: MissingEnum | User = (
            User(self._user, state) if self._user is not MISSING else MISSING
        )
        self.sort_value: MissingEnum | int = data.get('sort_value', MISSING)


class Attachment:
    def __init__(self, data: DiscordAttachment, state: State) -> None:
        self.id: Snowflake = Snowflake(data['id'])
        self.filename: str = data['filename']
        self.description: str | MissingEnum = data.get('description', MISSING)
        self.content_type: str | MissingEnum = data.get('content_type', MISSING)
        self.size: int = data.get('size')
        self.url: str = data.get('url')
        self.proxy_url: str = data.get('proxy_url')
        self.height: int | None | MissingEnum = data.get('height', MISSING)
        self.width: int | None | MissingEnum = data.get('width', MISSING)
        self.ephemeral: bool | MissingEnum = data.get('ephemeral', MISSING)

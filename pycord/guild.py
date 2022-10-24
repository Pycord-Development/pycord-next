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

from typing import Protocol

from discord_typings import EmojiData, GuildData, RoleData, RoleTagsData, Snowflake

from pycord.mixins import Hashable
from pycord.state import BaseConnectionState
from pycord.user import BaseUser


def _transform_into_roles(state: BaseConnectionState, roles: list[RoleData] | None = None) -> list["Role"] | None:
    if not roles:
        return

    ret = []
    for d in roles:
        ret.append(Role(d, state))

    return ret


class BaseGuild(Protocol):
    as_dict: GuildData
    _state: BaseConnectionState
    id: int
    name: str
    icon: str | None
    icon_hash: str | None
    splash: str | None
    discovery_splash: str | None
    is_owner: bool | None
    owner_id: int
    permissions: str
    afk_channel_id: int
    afk_timeout: int
    widget_enabled: bool | None
    widget_channel_id: int
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: list["BaseRole"]
    emojis: list["BaseEmoji"]
    features: list[str]
    mfa_level: int
    application_id: int | None
    system_channel_id: int | None
    system_channel_flags: int
    rules_channel_id: int | None

    def __init__(self, data: GuildData, state: BaseConnectionState):
        ...

    async def modify(
        self,
        reason: str | None = None,
        name: str = ...,
        verification_level: int | None = ...,
        default_message_notifications: int | None = ...,
        explicit_content_filter: int | None = ...,
        afk_channel_id: Snowflake | None = ...,
        afk_timeout: int = ...,
        icon: bytes | None = ...,
        owner_id: Snowflake = ...,
        splash: bytes | None = ...,
        discovery_splash: bytes | None = ...,
        banner: bytes | None = ...,
        system_channel_id: Snowflake | None = ...,
        system_channel_flags: int = ...,
        rules_channel_id: Snowflake | None = ...,
        public_updates_channel_id: Snowflake | None = ...,
        preferred_locale: str | None = ...,
        features: list[str] = ...,
        description: str | None = ...,
        premium_progress_bar_enabled: bool = ...,
    ) -> "BaseGuild":
        ...


class Guild(Hashable):
    def __init__(self, data: GuildData, state: BaseConnectionState):
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.name = data['name']
        self.icon = data['icon']
        self.icon_hash = data.get('icon_hash')
        self.splash = data['splash']
        self.discovery_splash = data['discovery_splash']
        self.is_owner = data.get('owner')
        # TODO: Possibly replace with user object.
        self.owner_id = int(data['owner_id'])
        # TODO: Set to permissions class
        self.permissions = data.get('permissions')
        # TODO: Possibly replace with channel object.
        self.afk_channel_id = int(data['afk_channel_id'])
        self.afk_timeout = data['afk_timeout']
        self.widget_enabled = data.get('widget_enabled')
        # TODO: Possibly replace with channel object.
        self.widget_channel_id = int(data.get('widget_channel_id'))
        self.verification_level = data['verification_level']
        self.default_message_notifications = data['default_message_notifications']
        self.explicit_content_filter = data['explicit_content_filter']
        # TODO: Replace with role classes
        self.roles = _transform_into_roles(data['roles'], state=state)  # type: ignore
        # TODO: Replace with emoji objects
        self.emojis = [Emoji(emoji) for emoji in data['emojis']]
        self.features = data['features']
        self.mfa_level = data['mfa_level']
        self.application_id = int(data['application_id'])
        # TODO: Possibly replace with channel object.
        self.system_channel_id = int(data['system_channel_id'])
        self.system_channel_flags = data['system_channel_flags']
        # TODO: Possibly replace with channel object.
        self.rules_channel_id = int(data['rules_channel_id'])

    async def modify(
        self,
        reason: str | None = None,
        name: str = ...,
        verification_level: int | None = ...,
        default_message_notifications: int | None = ...,
        explicit_content_filter: int | None = ...,
        afk_channel_id: Snowflake | None = ...,
        afk_timeout: int = ...,
        icon: bytes | None = ...,
        owner_id: Snowflake = ...,
        splash: bytes | None = ...,
        discovery_splash: bytes | None = ...,
        banner: bytes | None = ...,
        system_channel_id: Snowflake | None = ...,
        system_channel_flags: int = ...,
        rules_channel_id: Snowflake | None = ...,
        public_updates_channel_id: Snowflake | None = ...,
        preferred_locale: str | None = ...,
        features: list[str] = ...,
        description: str | None = ...,
        premium_progress_bar_enabled: bool = ...,
    ) -> "Guild":
        guild = Guild(
            await self._state._app.http.modify_guild(
                self.id,
                reason=reason,
                name=name,
                verification_level=verification_level,
                default_message_notifications=default_message_notifications,
                explicit_content_filter=explicit_content_filter,
                afk_channel_id=afk_channel_id,
                afk_timeout=afk_timeout,
                icon=icon,
                owner_id=owner_id,
                splash=splash,
                discovery_splash=discovery_splash,
                banner=banner,
                system_channel_id=system_channel_id,
                system_channel_flags=system_channel_flags,
                rules_channel_id=rules_channel_id,
                public_updates_channel_id=public_updates_channel_id,
                preferred_locale=preferred_locale,
                features=features,
                description=description,
                premium_progress_bar_enabled=premium_progress_bar_enabled,
            ),
            self._state,
        )

        if self.id in self._state.guilds:
            self._state.guilds[self.id] = guild

        return guild


class _RoleTags:
    def __init__(self, data: RoleTagsData | None) -> None:
        if data is not None:
            self.bot_id = data.get('bot_id')
            self.integration_id = data.get('integration_id')
            self.premium_subscriber = data.get('premium_subscriber')


class BaseRole(Protocol):
    as_dict: RoleData
    _state: BaseConnectionState

    id: int
    name: str
    color: int
    hoist: bool
    icon: str | None
    unicode_emoji: str | None
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: _RoleTags

    def __init__(self, data: RoleData, state: BaseConnectionState) -> None:
        pass


class Role(BaseRole, Hashable):
    def __init__(self, data: RoleData, state: BaseConnectionState) -> None:
        self.as_dict = data
        self._state = state

        self.id = int(data['id'])
        self.name = data['name']
        self.color = data['color']
        self.hoist = data['hoist']
        # TODO: Replace with asset object
        self.icon = data.get('icon')
        self.unicode_emoji = data.get('unicode_emoji')
        self.position = data['position']
        # TODO: Replace with permissions object
        self.permissions = data['permissions']
        self.managed = data['managed']
        self.mentionable = data['mentionable']
        self.tags = _RoleTags(data.get('tags'))


class BaseEmoji(Protocol):
    _state: BaseConnectionState

    id: int
    name: str
    roles: list[int]
    user: BaseUser | None
    required_colons: bool | None
    managed: bool | None
    animated: bool | None
    available: bool | None

    def __init__(self, data: EmojiData, state: BaseConnectionState) -> None:
        pass

    async def from_guild(self, guild: Guild) -> list["BaseEmoji"]:
        pass


class Emoji(BaseEmoji, Hashable):
    def __init__(self, data: EmojiData, state: BaseConnectionState) -> None:
        self._state = state
        # not sure why pyright hates this?
        self.id = int(data.get('id'))
        self.name = data['name']
        self.roles = data.get('roles')
        user = data.get('user')
        self.user: BaseUser | None = state._app.models['user'](user, state) if user is not None else None
        self.require_colons = data.get('require_colons')
        self.managed = data.get('managed')
        self.animated = data.get('animated')
        self.available = data.get('available')

    async def from_guild(self, guild: Guild) -> list["Emoji"]:
        ...

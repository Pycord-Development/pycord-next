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

from discord_typings import EmojiData, GuildData, RoleData, RoleTagsData

from pycord.mixins import Hashable
from pycord.state import ConnectionState
from pycord.user import User


def _transform_into_roles(state: ConnectionState, roles: list[RoleData] | None = None) -> list["Role"] | None:
    if not roles:
        return

    ret = []
    for d in roles:
        ret.append(Role(d, state))

    return ret


class Guild(Hashable):
    def __init__(self, data: GuildData, state: ConnectionState):
        self.as_dict = data
        self._state = state

        self.id = data['id']
        self.name = data['name']
        self.icon = data['icon']
        self.icon_hash = data.get('icon_hash')
        self.splash = data['splash']
        self.discovery_splash = data['discovery_splash']
        self.owner = data.get('owner')
        # TODO: Possibly replace with user object.
        self.owner_id = data['owner_id']
        # TODO: Set to permissions class
        self.permissions = data.get('permissions')
        # TODO: Possibly replace with channel object.
        self.afk_channel_id = data['afk_channel_id']
        self.afk_timeout = data['afk_timeout']
        self.widget_enabled = data.get('widget_enabled')
        # TODO: Possibly replace with channel object.
        self.widget_channel_id = data.get('widget_channel_id')
        self.verification_level = data['verification_level']
        self.default_message_notifications = data['default_message_notifications']
        self.explicit_content_filter = data['explicit_content_filter']
        # TODO: Replace with role classes
        self.roles = _transform_into_roles(data['roles'], state=state)  # type: ignore
        # TODO: Replace with emoji objects
        self.emojis = data['emojis']
        self.features = data['features']
        self.mfa_level = data['mfa_level']
        self.application_id = data['application_id']
        # TODO: Possibly replace with channel object.
        self.system_channel_id = data['system_channel_id']
        self.system_channel_flags = data['system_channel_flags']
        # TODO: Possibly replace with channel object.
        self.rules_channel_id = data['rules_channel_id']


class _RoleTags:
    def __init__(self, data: RoleTagsData | None) -> None:
        if data is not None:
            self.bot_id = data.get('bot_id')
            self.integration_id = data.get('integration_id')
            self.premium_subscriber = data.get('premium_subscriber')


class Role(Hashable):
    def __init__(self, data: RoleData, state: ConnectionState) -> None:
        self.as_dict = data
        self._state = state

        self.id = data['id']
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


class Emoji(Hashable):
    def __init__(self, data: EmojiData, state: ConnectionState) -> None:
        self._state = state
        # not sure why pyright hates this?
        self.id = data['id']  # type: ignore
        self.name = data['name']
        self.roles = data.get('roles')
        user = data.get('user')
        self.user: User | None = User(user, state) if user is not None else None
        self.require_colons = data.get('require_colons')
        self.managed = data.get('managed')
        self.animated = data.get('animated')
        self.available = data.get('available')

    def from_guild(self) -> list["Emoji"]:
        ...

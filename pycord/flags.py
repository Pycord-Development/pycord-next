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

from collections.abc import Callable
from typing import Literal, TypeVar

F = TypeVar('F', bound='Flags')
FF = TypeVar('FF')

__all__ = [
    'Intents',
    'Permissions',
    'ChannelFlags',
    'MessageFlags',
    'SystemChannelFlags',
    'ApplicationFlags',
    'UserFlags',
]


class flag:
    def __init__(self, func: Callable):
        self.value: int = func(None)
        self.__doc__ = func.__doc__

    def __get__(self, instance: F | None, _: type[F]) -> int | bool:
        return instance._has_flag(self.value) if instance else self.value

    def __set__(self, instance: F, value: bool) -> None:
        instance._overwrite_flag(flag=self.value, value=value)


class Flags:
    _IGNORED: list[str] = []

    def __init__(self, **flags_named: bool) -> None:
        self._flag_overwrites: list[tuple[int, bool]] = []

        for name, value in flags_named.items():
            if name.startswith('_'):
                raise AttributeError('Flags cannot be private')

            if not hasattr(self, name):
                raise AttributeError(f'Flag {repr(name)} does not exist')

            if name == 'as_bit':
                raise AttributeError('as_bit is not a flag')

            flag_value = getattr(self.__class__, name)
            self._overwrite_flag(flag_value, value)

    def _has_flag(self, flag: int) -> bool:
        return next(
            (
                overwrite[1]
                for overwrite in self._flag_overwrites
                if overwrite[0] == flag
            ),
            False,
        )

    def _overwrite_flag(self, flag: int, value: bool) -> None:
        if self._has_flag(flag=flag):
            self._flag_overwrites.remove((flag, value))

        self._flag_overwrites.append((flag, value))

    @staticmethod
    def _valid_flags(flagcls) -> dict[str, Literal[True]]:
        return {
            v: True
            for v in dir(flagcls)
            if not v.startswith('_')
            and v != 'as_bit'
            and v != 'mro'
            and v not in flagcls._IGNORED
        }

    @classmethod
    def _from_value(cls: type[FF], value: int | str) -> FF:
        value = int(value)
        valid_flag_names = cls._valid_flags(cls)
        valid_flags: dict[str, int] = {
            v: getattr(cls, v) for v, n in valid_flag_names.items()
        }
        parse: dict[str, Literal[True]] = {
            name: True for name, v in valid_flags.items() if (value & v)
        }

        return cls(**parse)

    @property
    def as_bit(self) -> int:
        return sum(
            overwrite[0] for overwrite in self._flag_overwrites if overwrite[1] is True
        )


class Intents(Flags):
    _IGNORED: list[str] = ['all', 'unpriv', 'priv']

    @flag
    def guilds(self) -> bool | int:
        return 1 << 0

    @flag
    def guild_members(self) -> bool | int:
        return 1 << 1

    @flag
    def guild_bans(self) -> bool | int:
        return 1 << 2

    @flag
    def guild_emojis_and_stickers(self) -> bool | int:
        return 1 << 3

    @flag
    def guild_integrations(self) -> bool | int:
        return 1 << 4

    @flag
    def guild_webhooks(self) -> bool | int:
        return 1 << 5

    @flag
    def guild_invites(self) -> bool | int:
        return 1 << 6

    @flag
    def guild_voice_states(self) -> bool | int:
        return 1 << 7

    @flag
    def guild_presences(self) -> bool | int:
        return 1 << 8

    @flag
    def guild_messages(self) -> bool | int:
        return 1 << 9

    @flag
    def guild_message_reactions(self) -> bool | int:
        return 1 << 10

    @flag
    def guild_message_typing(self) -> bool | int:
        return 1 << 11

    @flag
    def direct_messages(self) -> bool | int:
        return 1 << 12

    @flag
    def direct_message_reactions(self) -> bool | int:
        return 1 << 13

    @flag
    def direct_message_typing(self) -> bool | int:
        return 1 << 14

    @flag
    def message_content(self) -> bool | int:
        return 1 << 15

    @flag
    def guild_scheduled_events(self) -> bool | int:
        return 1 << 16

    @flag
    def auto_moderation_configuration(self) -> bool | int:
        return 1 << 20

    @flag
    def auto_moderation_execution(self) -> bool | int:
        return 1 << 21

    @classmethod
    def all(cls) -> Intents:
        valid_intents = cls._valid_flags(Intents)
        return cls(**valid_intents)

    @classmethod
    def priv(cls) -> Intents:
        return cls(message_content=True, guild_members=True, guild_presences=True)

    @classmethod
    def unpriv(cls) -> Intents:
        self = cls.all()
        self.message_content = False
        self.guild_members = False
        self.guild_presences = False
        return self


class Permissions(Flags):
    @flag
    def create_instant_invite(self) -> bool | int:
        return 1 << 0

    @flag
    def kick_members(self) -> bool | int:
        return 1 << 1

    @flag
    def ban_member(self) -> bool | int:
        return 1 << 2

    @flag
    def administrator(self) -> bool | int:
        return 1 << 3

    @flag
    def manage_channels(self) -> bool | int:
        return 1 << 4

    @flag
    def manage_guild(self) -> bool | int:
        return 1 << 5

    @flag
    def add_reactions(self) -> bool | int:
        return 1 << 6

    @flag
    def view_audit_log(self) -> bool | int:
        return 1 << 7

    @flag
    def priority_speaker(self) -> bool | int:
        return 1 << 8

    @flag
    def stream(self) -> int | bool:
        return 1 << 9

    @flag
    def view_channel(self) -> int | bool:
        return 1 << 10

    @flag
    def send_messages(self) -> int | bool:
        return 1 << 11

    @flag
    def send_tts_messages(self) -> int | bool:
        return 1 << 12

    @flag
    def manage_messages(self) -> bool | int:
        return 1 << 13

    @flag
    def embed_links(self) -> bool | int:
        return 1 << 14

    @flag
    def attach_files(self) -> bool | int:
        return 1 << 15

    @flag
    def read_message_history(self) -> bool | int:
        return 1 << 16

    @flag
    def mention_everyone(self) -> bool | int:
        return 1 << 17

    @flag
    def use_external_emojis(self) -> bool | int:
        return 1 << 18

    @flag
    def view_guild_insights(self) -> bool | int:
        return 1 << 19

    @flag
    def connect(self) -> bool | int:
        return 1 << 20

    @flag
    def speak(self) -> bool | int:
        return 1 << 21

    @flag
    def mute_members(self) -> bool | int:
        return 1 << 22

    @flag
    def deafen_members(self) -> bool | int:
        return 1 << 23

    @flag
    def move_members(self) -> bool | int:
        return 1 << 24

    @flag
    def use_vad(self) -> bool | int:
        return 1 << 25

    @flag
    def change_nickname(self) -> bool | int:
        return 1 << 26

    @flag
    def manage_nicknames(self) -> bool | int:
        return 1 << 27

    @flag
    def manage_roles(self) -> bool | int:
        return 1 << 28

    @flag
    def manage_webhooks(self) -> bool | int:
        return 1 << 29

    @flag
    def manage_emojis_and_stickers(self) -> bool | int:
        return 1 << 30

    @flag
    def use_application_commands(self) -> bool | int:
        return 1 << 31

    @flag
    def request_to_speak(self) -> bool | int:
        return 1 << 32

    @flag
    def manage_events(self) -> bool | int:
        return 1 << 33

    @flag
    def manage_threads(self) -> bool | int:
        return 1 << 34

    @flag
    def create_public_threads(self) -> bool | int:
        return 1 << 35

    @flag
    def create_private_threads(self) -> bool | int:
        return 1 << 36

    @flag
    def use_external_stickers(self) -> bool | int:
        return 1 << 37

    @flag
    def send_messages_in_threads(self) -> bool | int:
        return 1 << 38

    @flag
    def use_embedded_activities(self) -> bool | int:
        return 1 << 39

    @flag
    def moderate_members(self) -> bool | int:
        return 1 << 40


class SystemChannelFlags(Flags):
    @flag
    def suppress_join_notifications(self) -> bool | int:
        return 1 << 0

    @flag
    def suppress_premium_subscriptions(self) -> bool | int:
        return 1 << 1

    @flag
    def suppress_guild_reminder_notifications(self) -> bool | int:
        return 1 << 2

    @flag
    def suppress_guild_reminder_notifications(self) -> bool | int:
        return 1 << 3


class ApplicationFlags(Flags):
    @flag
    def gateway_presence(self) -> bool | int:
        return 1 << 12

    @flag
    def gateway_presence_limited(self) -> bool | int:
        return 1 << 13

    @flag
    def gateway_guild_members(self) -> bool | int:
        return 1 << 14

    @flag
    def gateway_guild_members_limited(self) -> bool | int:
        return 1 << 15

    @flag
    def verification_pending_guild_limit(self) -> bool | int:
        return 1 << 16

    @flag
    def embedded(self) -> bool | int:
        return 1 << 17

    @flag
    def gateway_message_content(self) -> bool | int:
        return 1 << 18

    @flag
    def gateway_message_content_limited(self) -> bool | int:
        return 1 << 19

    @flag
    def application_command_badge(self) -> bool | int:
        return 1 << 23

    @flag
    def active(self) -> bool | int:
        return 1 << 24


class ChannelFlags(Flags):
    @flag
    def pinned(self) -> bool | int:
        return 1 << 1

    @flag
    def require_tag(self) -> bool | int:
        return 1 << 4


class MessageFlags(Flags):
    @flag
    def crossposted(self) -> bool | int:
        return 1 << 0

    @flag
    def is_crossposted(self) -> bool | int:
        return 1 << 1

    @flag
    def suppress_embeds(self) -> bool | int:
        return 1 << 2

    @flag
    def source_message_deleted(self) -> bool | int:
        return 1 << 3

    @flag
    def urgent(self) -> bool | int:
        return 1 << 4

    @flag
    def has_thread(self) -> bool | int:
        return 1 << 5

    @flag
    def ephemeral(self) -> bool | int:
        return 1 << 6

    @flag
    def loading(self) -> bool | int:
        return 1 << 7

    @flag
    def failed_to_mention_some_roles_in_thread(self) -> bool | int:
        return 1 << 8


class UserFlags(Flags):
    @flag
    def staff(self) -> bool | int:
        return 1 << 0

    @flag
    def partner(self) -> bool | int:
        return 1 << 1

    @flag
    def hypesquad(self) -> bool | int:
        return 1 << 2

    @flag
    def bug_hunter_level_1(self) -> bool | int:
        return 1 << 3

    @flag
    def hypesquad_online_house_1(self) -> bool | int:
        return 1 << 6

    @flag
    def hypesquad_online_house_2(self) -> bool | int:
        return 1 << 7

    @flag
    def hypesquad_online_house_3(self) -> bool | int:
        return 1 << 8

    @flag
    def premium_early_supporter(self) -> bool | int:
        return 1 << 9

    @flag
    def team_pseudo_user(self) -> bool | int:
        return 1 << 10

    @flag
    def bug_hunter_level_2(self) -> bool | int:
        return 1 << 14

    @flag
    def verified_bot(self) -> bool | int:
        return 1 << 16

    @flag
    def verified_developer(self) -> bool | int:
        return 1 << 17

    @flag
    def certified_moderator(self) -> bool | int:
        return 1 << 18

    @flag
    def bot_http_interactions(self) -> bool | int:
        return 1 << 19

    @flag
    def active_developer(self) -> bool | int:
        return 1 << 22

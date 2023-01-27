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


from typing import TYPE_CHECKING, Any

from ..channel import Channel, Thread, identify_channel
from ..guild import Guild
from ..scheduled_event import ScheduledEvent
from ..stage_instance import StageInstance
from .event_manager import Event

if TYPE_CHECKING:
    from ..state import State


class GuildCreate(Event):
    _name = 'GUILD_CREATE'

    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        self.guild = Guild(data, state=state)
        self.channels: list[Channel] = [
            identify_channel(c, state) for c in data['channels']
        ]
        self.threads: list[Thread] = [
            identify_channel(c, state) for c in data['threads']
        ]
        self.stage_instances: list[StageInstance] = [
            StageInstance(st, state) for st in data['stage_instances']
        ]
        self.guild_scheduled_events: list[ScheduledEvent] = [
            ScheduledEvent(se, state) for se in data['guild_scheduled_events']
        ]

        await (state.store.sift('guilds')).insert(
            [self.guild.id], self.guild.id, self.guild
        )

        for channel in self.channels:
            await (state.store.sift('channels')).insert(
                [self.guild.id], channel.id, channel
            )

        for thread in self.threads:
            await (state.store.sift('threads')).insert(
                [self.guild.id, thread.parent_id], thread.id, thread
            )

        for stage in self.stage_instances:
            await (state.store.sift('stages')).insert(
                [stage.channel_id, self.guild.id, stage.guild_scheduled_event_id],
                stage.id,
                stage,
            )

        for scheduled_event in self.guild_scheduled_events:
            await (state.store.sift('scheduled_events')).insert(
                [
                    scheduled_event.channel_id,
                    scheduled_event.creator_id,
                    scheduled_event.entity_id,
                    self.guild.id,
                ],
                scheduled_event.id,
                scheduled_event,
            )

        return False


class GuildAvailable(GuildCreate):
    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        await super()._async_load(data, state)

        if self.guild.id in state._available_guilds:
            return True
        else:
            return False


class GuildJoin(GuildCreate):
    async def _async_load(self, data: dict[str, Any], state: 'State') -> bool:
        await super()._async_load(data, state)

        if self.guild.id not in state._available_guilds:
            return True
        else:
            return False

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

from datetime import datetime

from discord_typings import AllowedMentionsData, ComponentData, EmbedData, PartialAttachmentData, Snowflake

from pycord.file import File
from pycord.generators import channel_history_generator
from pycord.state import ConnectionState
from pycord.channel_typing import Typing
from pycord.utils import datetime_to_snowflake

# TODO: Replace raw data from discord_typings with models

class Messageable:
    """Represents a raw channel that you can send messages in and read messages from."""
    __slots__ = ()

    _state: ConnectionState
    pins_supported: bool = True

    async def _get_channel_id(self) -> Snowflake:
        raise NotImplementedError

    async def send(
        self, 
        content: str = ..., 
        *,
        tts: bool = ...,
        embeds: list[EmbedData] = ...,
        allowed_mentions: AllowedMentionsData = ...,
        components: list[ComponentData] = ...,
        sticker_ids: list[Snowflake] = ...,
        files: list[File] = ...,
        flags: int = ...,
    ):
        """Sends a message in this channel.

        All parameters are not required, however, one of the `content`, `embeds`, 
        `sticker_ids`, and `files` parameters have to be provided.

        Parameters
        ----------
        content: :class:`str`
            The content of this message.
        tts: :class:`bool`
            Whether or not this message should be played via text-to-speech.
        embeds: list[:class:`EmbedData`]
            The embeds of this message.
        allowed_mentions: :class:`AllowedMentionsData`
            The allowed mentions of this message.
        """
        return await self._state._app.http.create_message(
            await self._get_channel_id(),
            content=content,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
            sticker_ids=sticker_ids,
            files=files,
            flags=flags
        )

    async def get_messages(
        self, 
        *, 
        around: Snowflake | datetime = ...,
        before: Snowflake | datetime = ..., 
        after: Snowflake | datetime = ..., 
        limit: int | None = 50
    ):
        """Gets all messages from a certain time.

        Parameters
        ----------
        around: :class:`Snowflake` | :class:`datetime`
            Around the given time that the messages should be fetched from.
        before: :class:`Snowflake` | :class:`datetime`
            Before the given time that the messages should be fetched from.
        after: :class:`Snowflake` | :class:`datetime`
            After the given time that the messages should be fetched from.
        limit: :class:`int` | :class:`None`
            The limit of the amount of messages to grab. If set to :class:`None`, then
            all of the messages matching the conditions provided are fetched. Set to 50 
            by default.

        Returns
        -------
        :class:`MessageableHistoryGenerator`
            A generator that automatically handles grabbing the messages with the met
            conditions.
        """
        if isinstance(around, datetime):
            around = datetime_to_snowflake(around)
        if isinstance(before, datetime):
            before = datetime_to_snowflake(before)
        if isinstance(after, datetime):
            after = datetime_to_snowflake(after)

        return channel_history_generator(
            self,
            limit,
            around,
            before,
            after
        )

    async def purge_messages(
        self, 
        *, 
        around: Snowflake | datetime = ..., 
        before: Snowflake | datetime = ..., 
        after: Snowflake | datetime = ...,
        limit: int = 50,
        reason: str | None = None,
    ):
        """Purges messages that were sent before, around, or after a certain time.

        Parameters
        ----------
        around: Snowflake | :class:`datetime`
            The target messages that were sent around this time.
        before: Snowflake | :class:`datetime`
            The target messages that were sent before this time.
        after: Snowflake | :class:`datetime`
            The target messages that were sent after ths time.
        limit: int
            The limit of the amount of messages that can be purged. Default is 50, max is 100.
        reason: str | None
            The reason for purging these messages. Default is None.
        """
        if isinstance(around, datetime):
            around = datetime_to_snowflake(around)
        if isinstance(before, datetime):
            before = datetime_to_snowflake(before)
        if isinstance(after, datetime):
            after = datetime_to_snowflake(after)

        msgs = await self.get_messages(around=around, before=before, after=after, limit=limit)
        ids = [msg['id'] async for msg in msgs]
        
        await self._state._app.http.bulk_delete_messages(
            await self._get_channel_id(),
            messages=ids,
            reason=reason,
        )

    async def get_pins(self):
        """Gets all the pinned messages from this Messageable. 
        
        Returns
        -------
        list[:class:`MessageData`]
            The raw message data of the pinned messages.

        Raises
        ------
        :class:`TypeError`
            This implementation of Messageable doesn't support pinned messages.
        """
        if self.pins_supported:
            return await self._state._app.http.get_pinned_messages(await self._get_channel_id())
        else:
            raise TypeError(f'{self.__class__.__name__} does not support pinned messages!')

    async def trigger_typing(self):
        """Triggers the typing indicator for this messageable.
        
        This should be accompanied with the `async with` statement in order to actually trigger the 
        typing indicator.

        Returns
        -------
        :class:`.Typing`
            The context manager for the typing indicator.
        """
        return Typing(self)
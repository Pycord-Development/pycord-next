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
from urllib.parse import quote

from ...file import File
from ...snowflake import Snowflake
from ...types import Attachment, Emoji, User
from ...types.channel import AllowedMentions
from ...types.component import Component
from ...types.embed import Embed
from ...types.message import Message, MessageReference
from ...missing import MISSING, MissingEnum
from ...utils import remove_undefined
from ..route import Route
from .base import BaseRouter


class Messages(BaseRouter):
    async def create_message(
        self,
        channel_id: Snowflake,
        *,
        content: str | MissingEnum = MISSING,
        nonce: int | str | MissingEnum = MISSING,
        tts: bool | MissingEnum = MISSING,
        embeds: list[Embed] | MissingEnum = MISSING,
        allowed_mentions: AllowedMentions | MissingEnum = MISSING,
        message_reference: MessageReference | MissingEnum = MISSING,
        components: list[Component] | MissingEnum = MISSING,
        sticker_ids: list[Snowflake] | MissingEnum = MISSING,
        files: list[File] | MissingEnum = MISSING,
        flags: int | MissingEnum = MISSING,
    ) -> Message:
        data = {
            'content': content,
            'nonce': nonce,
            'tts': tts,
            'embeds': embeds,
            'allowed_mentions': allowed_mentions,
            'message_reference': message_reference,
            'components': components,
            'sticker_ids': sticker_ids,
            'flags': flags,
        }

        return await self.request(
            'POST',
            Route('/channels/{channel_id}/messages', channel_id=channel_id),
            remove_undefined(**data),
            files=files,
        )

    async def crosspost_message(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> Message:
        return await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/messages/{message_id}/crosspost',
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

    async def create_reaction(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str | Emoji,
    ) -> None:
        if isinstance(emoji, Emoji):
            emoji = f'{emoji.name}:{emoji.id}'
        emoji = quote(emoji)
        await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
        )

    async def delete_own_reaction(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str | Emoji,
    ) -> None:
        if isinstance(emoji, Emoji):
            emoji = f'{emoji.name}:{emoji.id}'
        emoji = quote(emoji)
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
        )

    async def delete_user_reaction(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str | Emoji,
        user_id: Snowflake,
    ) -> None:
        if isinstance(emoji, Emoji):
            emoji = f'{emoji.name}:{emoji.id}'
        emoji = quote(emoji)
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
                user_id=user_id,
            ),
        )

    async def get_reactions(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str | Emoji,
        *,
        limit: int | MissingEnum = MISSING,
        after: Snowflake | MissingEnum = MISSING,
    ) -> list[User]:
        if isinstance(emoji, Emoji):
            emoji = f'{emoji.name}:{emoji.id}'
        emoji = quote(emoji)
        params = {
            'limit': limit,
            'after': after,
        }
        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
            query_params=remove_undefined(**params),
        )

    async def delete_all_reactions(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions',
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

    async def delete_all_reactions_for_emoji(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str | Emoji,
    ) -> None:
        if isinstance(emoji, Emoji):
            emoji = f'{emoji.name}:{emoji.id}'
        emoji = quote(emoji)
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
        )

    async def edit_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        content: str | None | MissingEnum = MISSING,
        embeds: list[Embed] | None | MissingEnum = MISSING,
        flags: int | None | MissingEnum = MISSING,
        allowed_mentions: AllowedMentions | None | MissingEnum = MISSING,
        components: list[Component] | None | MissingEnum = MISSING,
        files: list[File] | None | MissingEnum = MISSING,
        attachments: list[Attachment] | None | MissingEnum = MISSING,
    ) -> Message:
        data = {
            'content': content,
            'embeds': embeds,
            'flags': flags,
            'allowed_mentions': allowed_mentions,
            'components': components,
            'attachments': attachments,
        }
        return await self.request(
            'PATCH',
            Route(
                '/channels/{channel_id}/messages/{message_id}',
                channel_id=channel_id,
                message_id=message_id,
            ),
            remove_undefined(**data),
            files=files,
        )

    async def delete_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}',
                channel_id=channel_id,
                message_id=message_id,
            ),
            reason=reason,
        )

    async def bulk_delete_messages(
        self,
        channel_id: Snowflake,
        message_ids: list[Snowflake],
        *,
        reason: str | None = None,
    ) -> None:
        await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/messages/bulk-delete',
                channel_id=channel_id,
            ),
            {
                'messages': message_ids,
            },
            reason=reason,
        )

    async def pin_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
    ) -> None:
        await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/pins/{message_id}',
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

    async def unpin_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
    ) -> None:
        await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/pins/{message_id}',
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

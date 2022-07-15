# Copyright (c) 2021-2022 VincentRPS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from discord_typings import (
    AllowedMentionsData,
    AttachmentData,
    ChannelData,
    ComponentData,
    EmbedData,
    MessageData,
    MessageReferenceData,
    PartialAttachmentData,
    PermissionOverwriteData,
    Snowflake,
)

from pycord.enums import ChannelType
from pycord.mixins import RouteCategoryMixin
from pycord.internal.http.route import Route

class ChannelRoutes(RouteCategoryMixin):
    async def get_channel(self, channel_id: Snowflake) -> ChannelData:
        return await self.request('GET', Route('/channels/{channel_id}', channel_id=channel_id))

    async def modify_channel(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        name: str  = ...,
        type: ChannelType  = ...,
        position: int | None  = ...,
        topic: str | None  = ...,
        nsfw: bool | None  = ...,
        rate_limit_per_user: int | None  = ...,
        bitrate: int | None  = ...,
        user_limit: int | None  = ...,
        permission_overwrites: list[PermissionOverwriteData] | None  = ...,
        parent_id: Snowflake | None  = ...,
        rtc_region: str | None  = ...,
        video_quality_mode: int | None  = ...,
        default_auto_archive_duration: int | None  = ...,
    ) -> ChannelData:
        payload = {}
        if name is not ...:
            payload['name'] = name
        if type is not ...:
            payload['type'] = int(type)
        if position is not ...:
            payload['position'] = position
        if topic is not ...:
            payload['topic'] = topic
        if nsfw is not ...:
            payload['nsfw'] = nsfw
        if rate_limit_per_user is not ...:
            payload['rate_limit_per_user'] = rate_limit_per_user
        if bitrate is not ...:
            payload['bitrate'] = bitrate
        if user_limit is not ...:
            payload['user_limit'] = user_limit
        if permission_overwrites is not ...:
            payload['permission_overwrites'] = permission_overwrites
        if parent_id is not ...:
            payload['parent_id'] = parent_id
        if rtc_region is not ...:
            payload['rtc_region'] = rtc_region
        if video_quality_mode is not ...:
            payload['video_quality_mode'] = video_quality_mode
        if default_auto_archive_duration is not ...:
            payload['default_auto_archive_duration'] = default_auto_archive_duration
        # TODO: Thread only parameters

        return await self.request('PATCH', Route('/channels/{channel_id}', channel_id=channel_id), payload, reason=reason)

    async def delete_channel(self, channel_id: Snowflake, *, reason: str | None = None) -> ChannelData:
        return await self.request('DELETE', Route('/channels/{channel_id}', channel_id=channel_id), reason=reason)

    async def get_channel_messages(
        self, 
        channel_id: Snowflake,
        *,
        around: Snowflake  = ...,
        before: Snowflake  = ...,
        after: Snowflake  = ...,
        limit: int = 50,
    ) -> list[MessageData]:
        if not 1 <= limit <= 100:
            raise ValueError('Limit must be between 1 and 100 (inclusive)')

        payload = {'limit': limit}
        if around is not ...:
            payload['around'] = around
        if before is not ...:
            payload['before'] = before
        if after is not ...:
            payload['after'] = after

        return await self.request('GET', Route('/channels/{channel_id}/messages', channel_id=channel_id), params=payload)

    async def get_channel_message(self, channel_id: Snowflake, message_id: Snowflake) -> MessageData:
        return await self.request('GET', Route('/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id))

    async def create_message(
        self,
        channel_id: Snowflake,
        *,
        content: str = ...,
        tts: bool = ...,
        embeds: list[EmbedData] = ...,
        allowed_mentions: AllowedMentionsData = ...,
        message_reference: MessageReferenceData = ...,
        components: list[ComponentData] = ...,
        sticker_ids: list[Snowflake] = ...,
        # TODO: files
        attachments: list[PartialAttachmentData] = ...,
        flags: int = ...,
    ) -> MessageData:
        # TODO: check if files are included
        if content is ... and embeds is ... and sticker_ids is ...:
            raise ValueError('One of content, embeds, or sticker_ids are required.')

        payload = {}
        if content is not ...:
            payload['content'] = content
        if tts is not ...:
            payload['tts'] = tts
        if embeds is not ...:
            payload['embeds'] = embeds
        if allowed_mentions is not ...:
            payload['allowed_mentions'] = allowed_mentions
        if message_reference is not ...:
            payload['message_reference'] = message_reference
        if components is not ...:
            payload['components'] = components
        if sticker_ids is not ...:
            payload['sticker_ids'] = sticker_ids
        if attachments is not ...:
            payload['attachments'] = attachments
        if flags is not ...:
            payload['flags'] = flags

        return await self.request('POST', Route('/channels/{channel_id}/messages', channel_id=channel_id), payload)

    async def crosspost_message(self, channel_id: Snowflake, message_id: Snowflake) -> MessageData:
        return await self.request('POST', Route('/channels/{channel_id}/messages/{message_id}/crosspost', channel_id=channel_id, message_id=message_id))

    async def create_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: str) -> None:
        return await self.request(
            'PUT', 
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
        )

    async def delete_own_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: str) -> None:
        return await self.request(
            'DELETE', 
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
        )

    async def delete_user_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: str, user_id: Snowflake) -> None:
        return await self.request(
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
        emoji: str,
        *,
        after: Snowflake = ...,
        limit: int = 25,
    ) -> None:
        if not 1 <= limit <= 100:
            raise ValueError('Limit must be between 1 and 100 (inclusive)')

        payload = {'limit':limit}
        if after is not ...:
            payload['after'] = after

        return await self.request(
            'GET', 
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
            payload
        )

    async def delete_all_reactions(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        return await self.request(
            'DELETE', 
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions',
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

    async def delete_all_reactions_for_emoji(self, channel_id: Snowflake, message_id: Snowflake, emoji: str) -> None:
        return await self.request(
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
        content: str | None = ...,
        embeds: list[EmbedData] | None = ...,
        flags: int | None = ...,
        allowed_mentions: AllowedMentionsData | None = ...,
        components: list[ComponentData] | None = ...,
        # TODO: files
        attachments: list[AttachmentData] | None = ...,
    ):
        payload = {}
        if content is not ...:
            payload['content'] = content
        if embeds is not ...:
            payload['embeds'] = embeds
        if flags is not ...:
            payload['flags'] = flags
        if allowed_mentions is not ...:
            payload['allowed_mentions'] = allowed_mentions
        if components is not ...:
            payload['components'] = components
        if attachments is not ...:
            payload['attachments'] = attachments

        return await self.request(
            'PATCH', 
            Route(
                '/channels/{channel_id}/messages/{message_id}', 
                channel_id=channel_id, 
                message_id=message_id
            ), 
            payload
        )

    async def delete_message(self, channel_id: Snowflake, message_id: Snowflake, *, reason: str | None = None):
        return await self.request('DELETE', Route('/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id), reason=reason)

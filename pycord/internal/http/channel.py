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

from datetime import datetime
from typing import Any
from discord_typings import (
    AllowedMentionsData,
    ChannelData,
    ComponentData,
    EmbedData,
    FollowedChannelData,
    InviteData,
    ListThreadsData,
    MessageData,
    MessageReferenceData,
    PartialAttachmentData,
    PermissionOverwriteData,
    Snowflake,
    ThreadChannelData,
    ThreadMemberData,
    UserData,
)

from pycord.enums import ChannelType, InviteTargetTypes
from pycord.file import File
from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin
from pycord.types import GuildChannelData


class ChannelRoutes(RouteCategoryMixin):
    async def get_channel(self, channel_id: Snowflake) -> ChannelData:
        """Get a channel by ID."""
        return await self.request('GET', Route('/channels/{channel_id}', channel_id=channel_id))

    async def modify_channel(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        name: str = ...,
        type: ChannelType = ...,
        position: int | None = ...,
        topic: str | None = ...,
        nsfw: bool | None = ...,
        rate_limit_per_user: int | None = ...,
        bitrate: int | None = ...,
        user_limit: int | None = ...,
        permission_overwrites: list[PermissionOverwriteData] | None = ...,
        parent_id: Snowflake | None = ...,
        rtc_region: str | None = ...,
        video_quality_mode: int | None = ...,
        default_auto_archive_duration: int | None = ...,
    ) -> GuildChannelData:
        """Update a channel's settings."""
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

        return await self.request(
            'PATCH', Route('/channels/{channel_id}', channel_id=channel_id), payload, reason=reason
        )

    async def delete_channel(self, channel_id: Snowflake, *, reason: str | None = None) -> ChannelData:
        """Delete a channel, or close a private message."""
        return await self.request('DELETE', Route('/channels/{channel_id}', channel_id=channel_id), reason=reason)

    async def get_channel_messages(
        self,
        channel_id: Snowflake,
        *,
        around: Snowflake = ...,
        before: Snowflake = ...,
        after: Snowflake = ...,
        limit: int = 50,
    ) -> list[MessageData]:
        """Returns the messages for a channel."""
        if not 1 <= limit <= 100:
            raise ValueError('Limit must be between 1 and 100 (inclusive)')

        payload = {'limit': limit}
        if around is not ...:
            payload['around'] = around
        if before is not ...:
            payload['before'] = before
        if after is not ...:
            payload['after'] = after

        return await self.request(
            'GET', Route('/channels/{channel_id}/messages', channel_id=channel_id), params=payload
        )

    async def get_channel_message(self, channel_id: Snowflake, message_id: Snowflake) -> MessageData:
        """Returns a specific message in the channel."""
        return await self.request(
            'GET', Route('/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id)
        )

    async def create_message(
        self,
        channel_id: Snowflake,
        *,
        content: str = None,
        tts: bool = None,
        embeds: list[EmbedData] = None,
        allowed_mentions: AllowedMentionsData = None,
        message_reference: MessageReferenceData = None,
        components: list[ComponentData] = None,
        sticker_ids: list[Snowflake] = None,
        files: list[File] | None = None,
        flags: int = None,
    ) -> MessageData:
        """Post a message to a guild text or DM channel."""
        if content is None and embeds is None and sticker_ids is None and not files:
            raise ValueError('One of content, embeds, sticker_ids, or files are required.')

        payload = {}
        if content is not None:
            payload['content'] = content
        if tts is not None:
            payload['tts'] = tts
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if message_reference is not None:
            payload['message_reference'] = message_reference
        if components is not None:
            payload['components'] = components
        if sticker_ids is not None:
            payload['sticker_ids'] = sticker_ids
        if flags is not None:
            payload['flags'] = flags

        if files is not None:
            payload = self._prepare_message_form(files, payload)
        else:
            files = []

        return await self.request(
            'POST',
            Route('/channels/{channel_id}/messages', channel_id=channel_id),
            payload,
            files=files
        )

    async def crosspost_message(self, channel_id: Snowflake, message_id: Snowflake) -> MessageData:
        """Crosspost a message in an Announcement Channel to following channels."""
        return await self.request(
            'POST',
            Route(
                '/channels/{channel_id}/messages/{message_id}/crosspost', channel_id=channel_id, message_id=message_id
            ),
        )

    async def create_reaction(self, channel_id: Snowflake, message_id: Snowflake, emoji: str) -> None:
        """Create a reaction for the message."""
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
        """Delete a reaction the current user has made for the message."""
        return await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
        )

    async def delete_user_reaction(
        self, channel_id: Snowflake, message_id: Snowflake, emoji: str, user_id: Snowflake
    ) -> None:
        """Deletes another user's reaction."""
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
        after: Snowflake = None,
        limit: int = 25,
    ) -> list[UserData]:
        """Get a list of users that reacted with this emoji."""
        if not 1 <= limit <= 100:
            raise ValueError('Limit must be between 1 and 100 (inclusive)')

        payload = {'limit': limit}
        if after is not None:
            payload['after'] = after

        return await self.request(
            'GET',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            ),
            payload,
        )

    async def delete_all_reactions(self, channel_id: Snowflake, message_id: Snowflake) -> None:
        """Deletes all reactions on a message."""
        return await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/messages/{message_id}/reactions',
                channel_id=channel_id,
                message_id=message_id,
            ),
        )

    async def delete_all_reactions_for_emoji(self, channel_id: Snowflake, message_id: Snowflake, emoji: str) -> None:
        """Deletes all the reactions for a given emoji on a message."""
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
        files: list[File] | None = None,
    ) -> MessageData:
        """Edit a previously sent message."""
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

        return await self.request(
            'PATCH',
            Route('/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id),
            payload,
            files=files
        )

    async def delete_message(self, channel_id: Snowflake, message_id: Snowflake, *, reason: str | None = None) -> None:
        """Delete a message."""
        return await self.request(
            'DELETE',
            Route('/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id),
            reason=reason,
        )

    async def bulk_delete_messages(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        messages: list[Snowflake]
    ) -> None:
        """Delete multiple messages in a single request."""
        if not 2 <= len(messages) <= 100:
            raise ValueError('The length of messages must be between 2 and 100 (inclusive)')

        payload = {'messages': messages}
        return await self.request(
            'POST',
            Route('/channels/{channel_id}/messages/bulk-delete', channel_id=channel_id),
            payload,
            reason=reason
        )

    async def edit_channel_permissions(
        self, 
        channel_id: Snowflake, 
        overwrite_id: Snowflake,
        *,
        reason: str | None = None,
        allow: str = '0',
        deny: str = '0',
        type: int,
    ) -> None:
        """Edit the channel permission overwrites for a user or role in a channel."""
        payload = {'allow': allow, 'deny': deny, 'type': type}
        return await self.request(
            'PUT',
            Route(
                '/channels/{channel_id}/permissions/{overwrite_id}',
                channel_id=channel_id,
                overwrite_id=overwrite_id
            ),
            payload
        )

    async def get_channel_invites(self, channel_id: Snowflake) -> list[InviteData]:
        """Returns a list of invites (with invite metadata) for the channel."""
        return await self.request('GET', Route('/channels/{channel_id}/invites', channel_id=channel_id))

    async def create_channel_invite(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        target_type: InviteTargetTypes = None,
        target_user_id: Snowflake = None,
        target_application_id: Snowflake = None,
    ) -> InviteData:
        """Create a new invite for the channel."""
        payload = {'max_age': max_age, 'max_uses': max_uses, 'temporary': temporary, 'unique': unique}
        if target_type is not None:
            payload['target_type'] = int(target_type)
        if target_user_id is not None:
            payload['target_user_id'] = target_user_id
        if target_application_id is not None:
            payload['target_application_id'] = target_application_id

        return await self.request(
            'POST',
            Route('/channels/{channel_id}/invites', channel_id=channel_id),
            payload,
            reason=reason
        )

    async def delete_channel_permission(
        self,
        channel_id: Snowflake,
        overwrite_id: Snowflake,
        *,
        reason: str | None = None
    ) -> None:
        """Delete a channel permission overwrite for a user or role in a channel."""
        return await self.request(
            'DELETE',
            Route(
                '/channels/{channel_id}/permissions/{overwrite_id}',
                channel_id=channel_id,
                overwrite_id=overwrite_id
            ),
            reason=reason
        )

    async def follow_news_channel(self, channel_id: Snowflake, *, webhook_channel_id: Snowflake) -> FollowedChannelData:
        """Follow an Announcement Channel to send messages to a target channel."""
        payload = {'webhook_channel_id': webhook_channel_id}
        return await self.request('POST', Route('/channels/{channel_id}/followers', channel_id=channel_id), payload)

    async def trigger_typing_indicator(self, channel_id: Snowflake) -> None:
        """Post a typing indicator for the specified channel."""
        return await self.request('POST', Route('/channels/{channel_id}/typing', channel_id=channel_id))

    async def get_pinned_messages(self, channel_id: Snowflake) -> list[MessageData]:
        """Returns all pinned messages in the channel as a list of messages."""
        return await self.request('GET', Route('/channels/{channel_id}/pins', channel_id=channel_id))

    async def pin_message(self, channel_id: Snowflake, message_id: Snowflake, *, reason: str | None = None) -> None:
        """Pin a message in a channel."""
        return await self.request(
            'PUT',
            Route('/channels/{channel_id}/pins/{message_id}', channel_id=channel_id, message_id=message_id),
            reason=reason
        )

    async def unpin_message(self, channel_id: Snowflake, message_id: Snowflake, *, reason: str | None = None) -> None:
        """Unpin a message in a channel."""
        return await self.request(
            'DELETE',
            Route('/channels/{channel_id}/pins/{message_id}', channel_id=channel_id, message_id=message_id),
            reason=reason
        )

    async def start_thread_from_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        reason: str | None = None,
        name: str,
        auto_archive_duration: int = None,
        rate_limit_per_user: int | None = None,
    ) -> ThreadChannelData:
        """Creates a new thread from an existing message."""
        payload = {'name': name}
        if auto_archive_duration is not None:
            payload['auto_archive_duration'] = auto_archive_duration
        if rate_limit_per_user is not None:
            payload['rate_limit_per_user'] = rate_limit_per_user

        return await self.request(
            'POST', 
            Route(
                '/channels/{channel_id}/messages/{message_id}/threads', 
                channel_id=channel_id, message_id=message_id
            ), 
            payload, 
            reason=reason
        )

    async def start_thread_without_message(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        name: str,
        auto_archive_duration: int = None,
        type: ChannelType = ChannelType.GUILD_PRIVATE_THREAD,
        invitable: bool = None,
        rate_limit_per_user: int | None = None,
    ) -> ThreadChannelData:
        """Creates a new thread that is not connected to an existing message."""
        payload = {'name': name, 'type': int(type)}
        if auto_archive_duration is not None:
            payload['auto_archive_duration'] = auto_archive_duration
        if invitable is not None:
            payload['invitable'] = invitable
        if rate_limit_per_user is not None:
            payload['rate_limit_per_user'] = rate_limit_per_user

        return await self.request(
            'POST', 
            Route('/channels/{channel_id}/threads', channel_id=channel_id), 
            payload, 
            reason=reason
        )

    async def start_thread_in_forum_channel(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        name: str,
        auto_archive_duration: int = None,
        rate_limit_per_user: int | None = None,
        content: str = None,
        embeds: list[EmbedData] = None,
        allowed_mentions: AllowedMentionsData = None,
        components: list[ComponentData] = None,
        sticker_ids: list[Snowflake] = None,
        files: list[File] | None = None,
        flags: int = None,
    ) -> ThreadChannelData:
        """Creates a new thread in a forum channel, and sends a message within the created thread."""
        if content is None and embeds is None and sticker_ids is None and not files:
            raise ValueError('One of content, embeds, sticker_ids, or files are required.')

        payload: dict[str, Any] = {'name': name}
        if auto_archive_duration is not None:
            payload['auto_archive_duration'] = auto_archive_duration
        if rate_limit_per_user is not None:
            payload['rate_limit_per_user'] = rate_limit_per_user
        if content is not None:
            payload['content'] = content
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if components is not None:
            payload['components'] = components
        if sticker_ids is not None:
            payload['sticker_ids'] = sticker_ids
        if flags is not None:
            payload['flags'] = flags

        return await self.request(
            'POST', 
            Route('/channels/{channel_id}/threads', channel_id=channel_id), 
            payload=payload, 
            reason=reason, 
            files=files
        )


    async def join_thread(self, channel_id: Snowflake) -> None:
        """Adds the current user to a thread."""
        return await self.request('PUT', Route('/channels/{channel_id}/thread-members/@me', channel_id=channel_id))

    async def add_thread_member(self, channel_id: Snowflake, user_id: Snowflake) -> None:
        """Adds another member to a thread."""
        return await self.request(
            'PUT',
            Route('/channels/{channel_id}/thread-members/{user_id}', channel_id=channel_id, user_id=user_id)
        )

    async def leave_thread(self, channel_id: Snowflake) -> None:
        """Removes the current user from a thread."""
        return await self.request(
            'DELETE',
            Route('/channels/{channel_id}/thread-members/@me', channel_id=channel_id)
        )

    async def remove_thread_member(self, channel_id: Snowflake, user_id: Snowflake) -> None:
        """Removes another member from a thread. """
        return await self.request(
            'DELETE',
            Route('/channels/{channel_id}/thread-members/{user_id}', channel_id=channel_id, user_id=user_id)
        )

    async def get_thread_member(self, channel_id: Snowflake, user_id: Snowflake) -> ThreadMemberData:
        """Returns a thread member for the specified user if they are a member of the thread."""
        return await self.request(
            'GET',
            Route('/channels/{channel_id}/thread-members/{user_id}', channel_id=channel_id, user_id=user_id)
        )

    async def list_thread_members(self, channel_id: Snowflake) -> list[ThreadMemberData]:
        """Returns a list of thread members that are members of the thread."""
        return await self.request('GET', Route('/channels/{channel_id}/thread-members', channel_id=channel_id))

    async def list_public_archived_threads(
        self,
        channel_id: Snowflake,
        *,
        before: datetime = None,
        limit: int = None
    ) -> ListThreadsData:
        """Returns archived threads in the channel that are public."""
        payload = {}
        if before is not None:
            payload['before'] = before
        if limit is not None:
            payload['limit'] = limit

        return await self.request(
            'GET',
            Route('/channels/{channel_id}/threads/archived/public', channel_id=channel_id),
            params=payload
        )

    async def list_private_archived_threads(
        self,
        channel_id: Snowflake,
        *,
        before: datetime = None,
        limit: int = None
    ) -> ListThreadsData:
        """Returns archived threads in the channel that are of type GUILD_PRIVATE_THREAD."""
        payload = {}
        if before is not None:
            payload['before'] = before
        if limit is not None:
            payload['limit'] = limit

        return await self.request(
            'GET',
            Route('/channels/{channel_id}/threads/archived/private', channel_id=channel_id),
            params=payload
        )

    async def list_joined_private_archived_threads(
        self,
        channel_id: Snowflake, *,
        before: datetime = None,
        limit: int = None
    ) -> ListThreadsData:
        """Returns archived threads in the channel that are of type GUILD_PRIVATE_THREAD, and the user has joined."""
        payload = {}
        if before is not None:
            payload['before'] = before
        if limit is not None:
            payload['limit'] = limit

        return await self.request(
            'GET',
            Route('/channels/{channel_id}/users/@me/threads/archived/private', channel_id=channel_id),
            params=payload
        )

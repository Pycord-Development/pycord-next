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
    ComponentData,
    EmbedData,
    MessageData,
    PartialAttachmentData,
    Snowflake,
    WebhookData,
)

from pycord import File
from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin
from pycord.utils import _convert_base64_from_bytes


class WebhookRoutes(RouteCategoryMixin):
    async def create_webhook(
        self,
        channel_id: Snowflake,
        *,
        name: str,
        avatar: bytes | None = None,
        reason: str | None = None,
    ) -> WebhookData:
        payload = {'name': name}
        if avatar is not None:
            payload['avatar'] = _convert_base64_from_bytes(avatar)

        return await self.request(
            'POST',
            Route('/channels/{channel_id}/webhooks', channel_id=channel_id),
            payload,
            reason=reason,
        )

    async def get_channel_webhooks(self, channel_id: Snowflake) -> list[WebhookData]:
        return await self.request('GET', Route('/channels/{channel_id}/webhooks', channel_id=channel_id))

    async def get_guild_webhooks(self, guild_id: Snowflake) -> list[WebhookData]:
        return await self.request('GET', Route('/guilds/{guild_id}/webhooks', guild_id=guild_id))

    async def get_webhook(self, webhook_id: Snowflake) -> WebhookData:
        return await self.request('GET', Route('/webhooks/{webhook_id}', webhook_id=webhook_id))

    async def get_webhook_with_token(self, webhook_id: Snowflake, webhook_token: str) -> WebhookData:
        return await self.request('GET', Route('/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id,
                                               webhook_token=webhook_token))

    async def modify_webhook(
        self,
        webhook_id: Snowflake,
        *,
        name: str = ...,
        avatar: bytes | None = ...,
        channel_id: Snowflake = ...,
        reason: str | None = None,
    ) -> WebhookData:
        payload = {}
        if name is not None:
            payload['name'] = name
        if avatar is not None:
            payload['avatar'] = _convert_base64_from_bytes(avatar)
        if channel_id is not ...:
            payload['channel_id'] = channel_id

        return await self.request(
            'PATCH',
            Route('/webhooks/{webhook_id}', webhook_id=webhook_id),
            payload,
            reason=reason,
        )

    async def modify_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        name: str = ...,
        avatar: bytes | None = ...,
    ) -> WebhookData:
        payload = {}
        if name is not None:
            payload['name'] = name
        if avatar is not None:
            payload['avatar'] = _convert_base64_from_bytes(avatar)

        return await self.request(
            'PATCH',
            Route('/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id, webhook_token=webhook_token),
            payload,
        )

    async def delete_webhook(self, webhook_id: Snowflake, reason: str | None = None) -> None:
        await self.request('DELETE', Route('/webhooks/{webhook_id}', webhook_id=webhook_id), reason=reason)

    async def delete_webhook_with_token(self, webhook_id: Snowflake, webhook_token: str) -> None:
        await self.request('DELETE', Route('/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id,
                                           webhook_token=webhook_token))

    async def execute_webhook(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        wait: bool | None = None,
        thread_id: Snowflake | None = None,
        content: str | None = None,
        username: str | None = None,
        avatar_url: str | None = None,
        tts: bool | None = None,
        embeds: list[EmbedData] | None = None,
        allowed_mentions: AllowedMentionsData | None = None,
        components: list[ComponentData] | None = None,
        files: list[File] | None = None,
        attachments: list[PartialAttachmentData] | None = None,
        flags: int | None = None,
        thread_name: str | None = None,
    ) -> None:
        params = {}
        if wait is not None:
            params['wait'] = wait
        if thread_id is not None:
            params['thread_id'] = thread_id

        payload = {}
        if content is not None:
            payload['content'] = content
        if username is not None:
            payload['username'] = username
        if avatar_url is not None:
            payload['avatar_url'] = avatar_url
        if tts is not None:
            payload['tts'] = tts
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if components is not None:
            payload['components'] = components
        if attachments is not None:
            payload['attachments'] = attachments
        if flags is not None:
            payload['flags'] = flags
        if thread_name is not None:
            payload['thread_name'] = thread_name

        await self.request(
            'POST',
            Route('/webhooks/{webhook_id}/{webhook_token}', webhook_id=webhook_id, webhook_token=webhook_token),
            payload,
            files=files,
        )

    async def get_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | None = None,
    ) -> MessageData:
        params = {}
        if thread_id is not None:
            params['thread_id'] = thread_id

        return await self.request('GET', Route(
            '/webhooks/{webhook_id}/{webhook_token}/{message_id}',
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id
        ), params=params)

    async def edit_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | None = None,
        content: str | None = None,
        embeds: list[EmbedData] | None = None,
        allowed_mentions: AllowedMentionsData | None = None,
        components: list[ComponentData] | None = None,
        files: list[File] | None = None,
        attachments: list[PartialAttachmentData] | None = None,
    ) -> MessageData:
        params = {}
        if thread_id is not None:
            params['thread_id'] = thread_id

        payload = {}
        if content is not None:
            payload['content'] = content
        if embeds is not None:
            payload['embeds'] = embeds
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        if components is not None:
            payload['components'] = components
        if attachments is not None:
            payload['attachments'] = attachments

        return await self.request(
            'PATCH',
            Route(
                '/webhooks/{webhook_id}/{webhook_token}/{message_id}',
                webhook_id=webhook_id,
                webhook_token=webhook_token,
                message_id=message_id
            ),
            payload,
            params=params,
            files=files,
        )

    async def delete_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | None = None,
    ) -> None:
        params = {}
        if thread_id is not None:
            params['thread_id'] = thread_id

        await self.request('DELETE', Route(
            '/webhooks/{webhook_id}/{webhook_token}/{message_id}',
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id
        ), params=params)

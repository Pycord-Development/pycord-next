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

from ...snowflake import Snowflake
from ...types import ATYPE, ApplicationCommandOption
from ...types.interaction import InteractionResponse
from ...undefined import UNDEFINED, UndefinedType
from ...utils import remove_undefined
from ..route import Route
from .base import BaseRouter


class ApplicationCommands(BaseRouter):
    async def get_global_application_commands(
        self, application_id: Snowflake, with_localizations: bool = False
    ):
        return await self.request(
            'GET',
            Route(
                '/applications/{application_id}/commands', application_id=application_id
            ),
            query_params={'with_localizations': str(with_localizations).lower()},
        )

    async def create_global_application_command(
        self,
        application_id: Snowflake,
        name: str,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOption] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: UndefinedType | bool | None = UNDEFINED,
        default_permission: bool | UndefinedType = UNDEFINED,
        type: ATYPE | UndefinedType = UNDEFINED,
    ):
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return await self.request(
            'POST',
            Route(
                '/applications/{application_id}/commands', application_id=application_id
            ),
            data=data,
        )

    async def edit_global_application_command(
        self,
        application_id: Snowflake,
        command_id: Snowflake,
        name: str | UndefinedType = UNDEFINED,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOption] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: UndefinedType | bool | None = UNDEFINED,
        default_permission: bool | UndefinedType = UNDEFINED,
        type: ATYPE | UndefinedType = UNDEFINED,
    ):
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return await self.request(
            'PATCH',
            Route(
                '/applications/{application_id}/commands/{command_id}',
                application_id=application_id,
                command_id=command_id,
            ),
            data=data,
        )

    async def delete_global_application_command(
        self,
        application_id: Snowflake,
        command_id: Snowflake,
    ):
        return await self.request(
            'DELETE',
            Route(
                '/applications/{application_id}/commands/{command_id}',
                application_id=application_id,
                command_id=command_id,
            ),
        )

    async def get_guild_application_commands(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        with_localizations: bool = False,
    ):
        return await self.request(
            'GET',
            Route(
                '/applications/{application_id}/guilds/{guild_id}/commands',
                application_id=application_id,
                guild_id=guild_id,
            ),
            query_params={'with_localizations': str(with_localizations).lower()},
        )

    async def create_guild_application_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        name: str,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOption] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: UndefinedType | bool | None = UNDEFINED,
        default_permission: bool | UndefinedType = UNDEFINED,
        type: ATYPE | UndefinedType = UNDEFINED,
    ):
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return await self.request(
            'POST',
            Route(
                '/applications/{application_id}/guilds/{guild_id}/commands',
                application_id=application_id,
                guild_id=guild_id,
            ),
            data=data,
        )

    async def edit_guild_application_command(
        self,
        application_id: Snowflake,
        command_id: Snowflake,
        guild_id: Snowflake,
        name: str | UndefinedType = UNDEFINED,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOption] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: UndefinedType | bool | None = UNDEFINED,
        default_permission: bool | UndefinedType = UNDEFINED,
        type: ATYPE | UndefinedType = UNDEFINED,
    ):
        data = remove_undefined(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            dm_permission=dm_permission,
            default_permission=default_permission,
            type=type,
        )

        return await self.request(
            'PATCH',
            Route(
                '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}',
                application_id=application_id,
                guild_id=guild_id,
                command_id=command_id,
            ),
            data=data,
        )

    async def delete_guild_application_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
    ):
        return await self.request(
            'DELETE',
            Route(
                '/applications/{application_id}/guilds/{guild_id}/commands/{command_id}',
                application_id=application_id,
                command_id=command_id,
                guild_id=guild_id,
            ),
        )

    async def create_interaction_response(
        self,
        interaction_id: Snowflake,
        interaction_token: str,
        response: InteractionResponse,
    ) -> None:
        await self.request(
            'POST',
            Route(
                '/interactions/{interaction_id}/{interaction_token}/callback',
                interaction_id=interaction_id,
                interaction_token=interaction_token,
            ),
            data=response,
        )

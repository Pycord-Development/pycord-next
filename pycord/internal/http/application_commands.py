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


from signal import default_int_handler
from discord_typings import Snowflake, ApplicationCommandData, ApplicationCommandOptionData

from pycord.internal.http.route import Route
from pycord.mixins import RouteCategoryMixin


class ApplicationCommandRoutes(RouteCategoryMixin):
    async def get_global_application_commands(
        self, 
        application_id: Snowflake,
        *,
        with_localizations: bool | None = None,
    ) -> list[ApplicationCommandData]:
        """Fetch all of the global commands for your application."""
        params = {}
        if with_localizations is not None:
            params['with_localizations'] = with_localizations

        return await self.request(
            'GET', 
            Route('applications/{application_id}/commands', application_id=application_id),
            params=params,
        )

    async def create_global_application_command(
        self,
        application_id: Snowflake,
        *,
        name: str,
        description: str,
        name_localizations: dict[str, str] | None = None,
        description_localizations: dict[str, str] | None = None,
        options: list[ApplicationCommandOptionData] | None = None,
        default_member_permissions: str | None = None,
        dm_permission: bool | None = None,
        command_type: int | None = None,
    ) -> ApplicationCommandData:
        """Create a new global command."""
        payload = {
            'name': name,
            'description': description,
        }
        if name_localizations is not None:
            payload['name_localizations'] = name_localizations
        if description_localizations is not None:
            payload['description_localizations'] = description_localizations
        if options is not None:
            payload['options'] = options
        if default_member_permissions is not None:
            payload['default_member_permissions'] = default_member_permissions
        if dm_permission is not None:
            payload['dm_permission'] = dm_permission
        if command_type is not None:
            payload['type'] = command_type

        return await self.request(
            'GET', 
            Route('applications/{application_id}/commands', application_id=application_id),
            payload,
        )
    
    async def get_global_application_command(
        self, 
        application_id: Snowflake,
        command_id: Snowflake,
    ) -> list[ApplicationCommandData]:
        """Fetch a global command for your application."""
        return await self.request(
            'GET', 
            Route(
                'applications/{application_id}/commands/{command_id}', 
                application_id=application_id,
                command_id=command_id,
            ),
        )
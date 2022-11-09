# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2021-present VincentRPS
# Copyright (c) 2022-present Pycord Development
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
from ...utils import UNDEFINED, UndefinedType, remove_undefined
from ..route import Route
from .base import BaseRouter


class ApplicationCommands(BaseRouter):
    async def get_global_application_commands(self, application_id: Snowflake, with_localizations: bool = False):
        if with_localizations:
            return await self.request(
                'GET',
                Route('/applications/{application_id}/commands?=with_localizations=true', application_id=application_id),
            )
        else:
            return await self.request('GET', Route('/applications/{application_id}/commands', application_id=application_id))

    async def create_global_application_command(
        self,
        application_id: Snowflake,
        name: str,
        name_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[str, str] | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOption] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: UNDEFINED | bool | None = UNDEFINED,
        default_permission: bool | UNDEFINED = UNDEFINED,
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
            'POST', Route('/applications/{application_id}/commands', application_id=application_id), data=data
        )

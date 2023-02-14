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
from datetime import datetime
from typing import Any, cast

from typing_extensions import Self

from .color import Color
from .types import (
    Author as DiscordAuthor,
    Embed as DiscordEmbed,
    Field as DiscordField,
    Footer as DiscordFooter,
    Image as DiscordImage,
    Provider as DiscordProvider,
    Thumbnail as DiscordThumbnail,
    Video as DiscordVideo,
)
from .undefined import UNDEFINED, UndefinedType
from .utils import remove_undefined


# pure data classes, no user interaction.
class Provider:
    def __init__(self, data: DiscordProvider) -> None:
        self.name: UndefinedType | str = data.get('name', UNDEFINED)
        self.url: UndefinedType | str = data.get('url', UNDEFINED)


class Video:
    def __init__(self, data: DiscordVideo) -> None:
        self.url: UndefinedType | str = data.get('url', UNDEFINED)
        self.proxy_url: UndefinedType | str = data.get('proxy_url', UNDEFINED)
        self.width: UndefinedType | int = data.get('width', UNDEFINED)
        self.height: UndefinedType | int = data.get('height', UNDEFINED)


class Thumbnail:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.proxy_url: str | UndefinedType = UNDEFINED
        self.height: UndefinedType | int = UNDEFINED
        self.width: UndefinedType | int = UNDEFINED

    @classmethod
    def _from_data(cls, data: DiscordThumbnail) -> 'Thumbnail':
        self = cls(data['url'])
        self.proxy_url = data.get('proxy_url', UNDEFINED)
        self.height = data.get('height', UNDEFINED)
        self.width = data.get('width', UNDEFINED)
        return self

    def _to_data(self) -> dict[str, Any]:
        return remove_undefined(url=self.url)


class Image:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.proxy_url: str | UndefinedType = UNDEFINED
        self.height: UndefinedType | int = UNDEFINED
        self.width: UndefinedType | int = UNDEFINED

    @classmethod
    def _from_data(cls, data: DiscordImage) -> 'Image':
        self = cls(data['url'])
        self.proxy_url = data.get('proxy_url', UNDEFINED)
        self.height = data.get('height', UNDEFINED)
        self.width = data.get('width', UNDEFINED)
        return self

    def _to_data(self) -> dict[str, Any]:
        return remove_undefined(url=self.url)


class Footer:
    def __init__(self, text: str, icon_url: str | UndefinedType = UNDEFINED) -> None:
        self.text = text
        self.icon_url = icon_url
        self.proxy_icon_url: UndefinedType | str = UNDEFINED

    @classmethod
    def _from_data(cls, data: DiscordFooter) -> 'Footer':
        self = cls(data['text'], data.get('icon_url', UNDEFINED))
        self.proxy_icon_url = data.get('proxy_icon_url', UNDEFINED)
        return self

    def _to_data(self) -> dict[str, Any]:
        return remove_undefined(text=self.text, icon_url=self.icon_url)


class Author:
    def __init__(
        self,
        name: str,
        icon_url: str | UndefinedType = UNDEFINED,
        url: str | UndefinedType = UNDEFINED,
    ) -> None:
        self.name = name
        self.url = url
        self.icon_url = icon_url
        self.proxy_icon_url: UndefinedType | str = UNDEFINED

    @classmethod
    def _from_data(cls, data: DiscordAuthor) -> 'Author':
        self = cls(
            data['name'], data.get('icon_url', UNDEFINED), data.get('url', UNDEFINED)
        )
        self.proxy_icon_url = data.get('proxy_icon_url', UNDEFINED)
        return self

    def _to_data(self) -> dict[str, Any]:
        return remove_undefined(name=self.name, url=self.url, icon_url=self.icon_url)


class Field:
    def __init__(
        self, name: str, value: str, inline: bool | UndefinedType = UNDEFINED
    ) -> None:
        self.name = name
        self.value = value
        self.inline = inline

    @classmethod
    def _from_data(cls, data: DiscordField) -> 'Field':
        return cls(data['name'], data['value'], data.get('field', UNDEFINED))

    def _to_data(self) -> dict[str, Any]:
        return remove_undefined(name=self.name, value=self.value, inline=self.inline)


# settable:
# footer
# fields
# image
# thumbnail
# author
# NOTE: this is the only class not having data being parsed in __init__ because of it being used mostly by users.
class Embed:
    def __init__(
        self,
        *,
        title: str,
        description: str | UndefinedType = UNDEFINED,
        url: str | UndefinedType = UNDEFINED,
        timestamp: datetime | UndefinedType = UNDEFINED,
        color: Color | UndefinedType = UNDEFINED,
        thumbnail: Thumbnail | UndefinedType = UNDEFINED,
        author: Author | UndefinedType = UNDEFINED,
        footer: Footer | UndefinedType = UNDEFINED,
        image: Image | UndefinedType = UNDEFINED,
        video: Video | UndefinedType = UNDEFINED,
        provider: Provider | UndefinedType = UNDEFINED,
        fields: list[Field] | None = None,
    ) -> None:
        if fields is None:
            fields = []
        self.thumbnail = thumbnail
        self.author = author
        self.footer = footer
        self.image = image
        self.fields = fields
        self.title = title
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color
        self.video = video
        self.provider = provider

    @classmethod
    def _from_data(cls, data: DiscordEmbed) -> Self:
        timestamp = (
            datetime.fromisoformat(raw_timestamp)
            if (raw_timestamp := data.get('timestamp')) is not None
            else UNDEFINED
        )
        color = (
            Color(raw_color)
            if (raw_color := data.get('color')) is not None
            else UNDEFINED
        )
        thumbnail = Thumbnail._from_data(raw_thumbnail) if (raw_thumbnail := data.get('thumbnail')) is not None else UNDEFINED  # type: ignore
        video = (
            Video(raw_video)
            if (raw_video := data.get('video')) is not None
            else UNDEFINED
        )
        provider = (
            Provider(raw_provider)
            if (raw_provider := data.get('provider')) is not None
            else UNDEFINED
        )
        author = Author._from_data(raw_author) if (raw_author := data.get('author')) is not None else UNDEFINED  # type: ignore
        footer = Footer._from_data(raw_footer) if (raw_footer := data.get('footer')) is not None else UNDEFINED  # type: ignore
        image = Image._from_data(raw_image) if (raw_image := data.get('image')) is not None else UNDEFINED  # type: ignore
        fields = [Field._from_data(field) for field in data.get('fields', [])]  # type: ignore

        self = cls(
            title=data.get('title', ''),
            description=data.get('description', UNDEFINED),
            url=data.get('url', UNDEFINED),
            timestamp=timestamp,
            color=color,
            footer=footer,
            image=image,
            thumbnail=thumbnail,
            author=author,
            fields=fields,
            video=video,
            provider=provider,
        )
        return self

    def _to_data(self) -> DiscordEmbed:
        color = self.color.value if self.color else None
        thumbnail = self.thumbnail._to_data() if self.thumbnail else UNDEFINED  # type: ignore
        author = self.author._to_data() if self.author else UNDEFINED  # type: ignore
        footer = self.footer._to_data() if self.footer else UNDEFINED  # type: ignore
        image = self.image._to_data() if self.image else UNDEFINED  # type: ignore
        fields = [field._to_data() for field in self.fields]  # type: ignore
        timestamp = self.timestamp.isoformat() if self.timestamp else UNDEFINED

        return cast(
            DiscordEmbed,
            remove_undefined(
                title=self.title,
                description=self.description,
                url=self.url,
                color=color,
                timestamp=timestamp,
                thumbnail=thumbnail,
                footer=footer,
                author=author,
                image=image,
                fields=fields,
            ),
        )

from __future__ import annotations

from discord_typings._resources._channel import (
    EmbedAuthorData, EmbedData, EmbedFieldData, EmbedFooterData, EmbedImageData, EmbedThumbnailData,
    EmbedVideoData,
)

from pycord import remove_undefined
from pycord.missing import Maybe, MISSING


class Embed:
    def __init__(
        self,
        title: Maybe[str] = MISSING,
        type: Maybe[str] = MISSING,
        description: Maybe[str] = MISSING,
        url: Maybe[str] = MISSING,
        timestamp: Maybe[str] = MISSING,
        color: Maybe[int] = MISSING,
        footer: Maybe[EmbedFooter] = MISSING,
        image: Maybe[EmbedImage] = MISSING,
        thumbnail: Maybe[EmbedThumbnail] = MISSING,
        video: Maybe[EmbedVideo] = MISSING,
        provider: Maybe[EmbedProvider] = MISSING,
        author: Maybe[EmbedAuthor] = MISSING,
        fields: Maybe[list[EmbedField]] = MISSING,
    ):
        self.title: Maybe[str] = title
        self.type: Maybe[str] = type
        self.description: Maybe[str] = description
        self.url: Maybe[str] = url
        self.timestamp: Maybe[str] = timestamp
        self.color: Maybe[int] = color
        self.footer: Maybe[EmbedFooter] = footer
        self.image: Maybe[EmbedImage] = image
        self.thumbnail: Maybe[EmbedThumbnail] = thumbnail
        self.video: Maybe[EmbedVideo] = video
        self.provider: Maybe[EmbedProvider] = provider
        self.author: Maybe[EmbedAuthor] = author
        self.fields: Maybe[list[EmbedField]] = fields

    def validate(self) -> None:
        if self.title is not MISSING and len(self.title) > 256:
            raise ValueError("Title cannot exceed 256 characters.")
        if self.description is not MISSING and len(self.description) > 2048:
            raise ValueError("Description cannot exceed 2048 characters.")
        if self.fields is not MISSING and len(self.fields) > 25:
            raise ValueError("Number of fields cannot exceed 25.")
        if self.footer is not MISSING:
            self.footer.validate()
        if self.author is not MISSING:
            self.author.validate()
        if self.fields is not MISSING:
            for field in self.fields:
                field.validate()
        if self.image is not MISSING:
            self.image.validate()
        if self.thumbnail is not MISSING:
            self.thumbnail.validate()
        if len(self) > 6000:
            raise ValueError("Total length of embed cannot exceed 6000 characters.")

    def to_dict(self, *, to_send: bool = False) -> EmbedData:
        if to_send:
            return remove_undefined(
                **{
                    "title": self.title,
                    "type": self.type,
                    "description": self.description,
                    "url": self.url,
                    "timestamp": self.timestamp,
                    "color": self.color,
                    "footer": self.footer.to_dict(to_send=True) if self.footer is not MISSING else MISSING,
                    "image": self.image.to_dict(to_send=True) if self.image is not MISSING else MISSING,
                    "thumbnail": self.thumbnail.to_dict(to_send=True) if self.thumbnail is not MISSING else MISSING,
                    "author": self.author.to_dict(to_send=True) if self.author is not MISSING else MISSING,
                    "fields": [field.to_dict() for field in self.fields] if self.fields is not MISSING else MISSING
                }
            )
        return remove_undefined(
            **{
                "title": self.title,
                "type": self.type,
                "description": self.description,
                "url": self.url,
                "timestamp": self.timestamp,
                "color": self.color,
                "footer": self.footer.to_dict() if self.footer is not MISSING else MISSING,
                "image": self.image.to_dict() if self.image is not MISSING else MISSING,
                "thumbnail": self.thumbnail.to_dict() if self.thumbnail is not MISSING else MISSING,
                "video": self.video.to_dict() if self.video is not MISSING else MISSING,
                "provider": self.provider.to_dict() if self.provider is not MISSING else MISSING,
                "author": self.author.to_dict() if self.author is not MISSING else MISSING,
                "fields": [field.to_dict() for field in self.fields] if self.fields is not MISSING else MISSING
            }
        )

    @classmethod
    def from_dict(cls, data: EmbedData) -> Embed:
        return cls(
            title=data.get("title", MISSING),
            type=data.get("type", MISSING),
            description=data.get("description", MISSING),
            url=data.get("url", MISSING),
            timestamp=data.get("timestamp", MISSING),
            color=data.get("color", MISSING),
            footer=EmbedFooter.from_dict(data.get("footer", {})),
            image=EmbedImage.from_dict(data.get("image", {})),
            thumbnail=EmbedThumbnail.from_dict(data.get("thumbnail", {})),
            video=EmbedVideo.from_dict(data.get("video", {})),
            provider=EmbedProvider.from_dict(data.get("provider", {})),
            author=EmbedAuthor.from_dict(data.get("author", {})),
            fields=[EmbedField.from_dict(field) for field in data.get("fields", [])]
        )

    def __len__(self):
        return len(self.title or "") + len(self.description or "") + sum(len(field) for field in self.fields or []) + \
            len(self.footer or "") + len(self.author or "")


class EmbedFooter:
    def __init__(self, *, text: str, icon_url: Maybe[str] = MISSING, proxy_icon_url: Maybe[str] = MISSING):
        self.text: str = text
        self.icon_url: Maybe[str] = icon_url
        self.proxy_icon_url: Maybe[str] = proxy_icon_url

    def validate(self) -> None:
        if len(self.text) > 2048:
            raise ValueError("Footer text cannot exceed 2048 characters.")
        if self.icon_url is not MISSING and not self.icon_url.startswith("https://") \
                and not self.icon_url.startswith("http://") and not self.icon_url.startswith("attachment://"):
            raise ValueError("Footer icon url must have a protocol of http, https, or attachment.")

    def to_dict(self, *, to_send: bool = False) -> EmbedFooterData:
        if to_send:
            return remove_undefined(**{"text": self.text, "icon_url": self.icon_url})
        return remove_undefined(
            **{
                "text": self.text,
                "icon_url": self.icon_url,
                "proxy_icon_url": self.proxy_icon_url
            }
        )

    @classmethod
    def from_dict(cls, data: EmbedFooterData) -> EmbedFooter:
        return cls(
            text=data["text"],
            icon_url=data.get("icon_url", MISSING),
            proxy_icon_url=data.get("proxy_icon_url", MISSING)
        )

    def __len__(self):
        return len(self.text)


class EmbedImage:
    def __init__(
        self, *, url: str, proxy_url: Maybe[str] = MISSING, height: Maybe[int] = MISSING,
        width: Maybe[int] = MISSING
    ):
        self.url: str = url
        self.proxy_url: Maybe[str] = proxy_url
        self.height: Maybe[int] = height
        self.width: Maybe[int] = width

    def validate(self) -> None:
        if not self.url.startswith("https://") and not self.url.startswith("http://") \
                and not self.url.startswith("attachment://"):
            raise ValueError("Image url must have a protocol of http, https, or attachment.")

    def to_dict(self, *, to_send: bool = False) -> EmbedImageData:
        if to_send:
            return {"url": self.url}
        return remove_undefined(
            **{
                "url": self.url,
                "proxy_url": self.proxy_url,
                "height": self.height,
                "width": self.width
            }
        )

    @classmethod
    def from_dict(cls, data: EmbedImageData) -> EmbedImage:
        return cls(
            url=data["url"],
            proxy_url=data.get("proxy_url", MISSING),
            height=data.get("height", MISSING),
            width=data.get("width", MISSING)
        )


class EmbedThumbnail:
    def __init__(
        self, *, url: str, proxy_url: Maybe[str] = MISSING, height: Maybe[int] = MISSING, width: Maybe[int] = MISSING
    ):
        self.url: str = url
        self.proxy_url: Maybe[str] = proxy_url
        self.height: Maybe[int] = height
        self.width: Maybe[int] = width

    def validate(self) -> None:
        if self.url is not MISSING and not self.url.startswith("https://") \
                and not self.url.startswith("http://") and not self.url.startswith("attachment://"):
            raise ValueError("Thumbnail url must have a protocol of http, https, or attachment.")

    def to_dict(self, *, to_send: bool = False) -> EmbedThumbnailData:
        if to_send:
            return {"url": self.url}
        return remove_undefined(
            **{
                "url": self.url,
                "proxy_url": self.proxy_url,
                "height": self.height,
                "width": self.width
            }
        )

    @classmethod
    def from_dict(cls, data: EmbedThumbnailData) -> EmbedThumbnail:
        return cls(
            url=data["url"],
            proxy_url=data.get("proxy_url", MISSING),
            height=data.get("height", MISSING),
            width=data.get("width", MISSING)
        )


class EmbedVideo:
    def __init__(
        self, *, url: Maybe[str] = MISSING, proxy_url: Maybe[str] = MISSING,
        height: Maybe[int] = MISSING, width: Maybe[int] = MISSING
    ):
        self.url: Maybe[str] = url
        self.proxy_url: Maybe[str] = proxy_url
        self.height: Maybe[int] = height
        self.width: Maybe[int] = width

    def to_dict(self) -> EmbedVideoData:
        return remove_undefined(
            **{
                "url": self.url,
                "proxy_url": self.proxy_url,
                "height": self.height,
                "width": self.width
            }
        )

    @classmethod
    def from_dict(cls, data: EmbedVideoData) -> EmbedVideo:
        return cls(
            url=data.get("url", MISSING),
            proxy_url=data.get("proxy_url", MISSING),
            height=data.get("height", MISSING),
            width=data.get("width", MISSING)
        )


class EmbedProvider:
    def __init__(self, *, name: Maybe[str] = MISSING, url: Maybe[str] = MISSING):
        self.name: Maybe[str] = name
        self.url: Maybe[str] = url

    def to_dict(self) -> dict[str, str]:
        return remove_undefined(**{"name": self.name, "url": self.url})

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> EmbedProvider:
        return cls(
            name=data.get("name", MISSING),
            url=data.get("url", MISSING),
        )


class EmbedAuthor:
    def __init__(
        self, *, name: str, url: Maybe[str] = MISSING, icon_url: Maybe[str] = MISSING,
        proxy_icon_url: Maybe[str] = MISSING
    ):
        self.name: str = name
        self.url: Maybe[str] = url
        self.icon_url: Maybe[str] = icon_url
        self.proxy_icon_url: Maybe[str] = proxy_icon_url

    def validate(self) -> None:
        if len(self.name) > 256:
            raise ValueError("Author name cannot exceed 256 characters.")
        if self.icon_url is not MISSING and not self.url.startswith("https://") \
                and not self.url.startswith("http://") and not self.url.startswith("attachment://"):
            raise ValueError("Author icon url must have a protocol of http, https, or attachment.")

    def to_dict(self, *, to_send: bool = False) -> EmbedAuthorData:
        if to_send:
            return remove_undefined(**{"name": self.name, "url": self.url, "icon_url": self.icon_url})
        return remove_undefined(
            **{
                "name": self.name,
                "url": self.url,
                "icon_url": self.icon_url,
                "proxy_icon_url": self.proxy_icon_url
            }
        )

    @classmethod
    def from_dict(cls, data: EmbedAuthorData) -> EmbedAuthor:
        return cls(
            name=data["name"],
            url=data.get("url", MISSING),
            icon_url=data.get("icon_url", MISSING),
            proxy_icon_url=data.get("proxy_icon_url", MISSING)
        )

    def __len__(self):
        return len(self.name)


class EmbedField:
    def __init__(self, *, name: str, value: str, inline: Maybe[bool] = MISSING):
        self.name: str = name
        self.value: str = value
        self.inline: Maybe[bool] = inline

    def validate(self) -> None:
        if len(self.name) > 256:
            raise ValueError("Field name cannot exceed 256 characters.")
        if len(self.value) > 1024:
            raise ValueError("Field value cannot exceed 1024 characters.")

    def to_dict(self) -> EmbedFieldData:
        return remove_undefined(**{"name": self.name, "value": self.value, "inline": self.inline})

    @classmethod
    def from_dict(cls, data: EmbedFieldData) -> EmbedField:
        return cls(
            name=data["name"],
            value=data["value"],
            inline=data.get("inline", MISSING)
        )

    def __len__(self):
        return len(self.name) + len(self.value)

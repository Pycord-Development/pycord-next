from discord_typings import Snowflake


class Route:
    def __init__(
        self,
        path: str,
        guild_id: Snowflake | None = None,
        channel_id: Snowflake | None = None,
        webhook_id: Snowflake | None = None,
        webhook_token: str | None = None,
        **parameters: str | int,
    ):
        self.path = path

        # major parameters
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.webhook_id = webhook_id
        self.webhook_token = webhook_token

        self.parameters = parameters

    def merge(self, url: str):
        return url + self.path.format(
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            webhook_id=self.webhook_id,
            webhook_token=self.webhook_token,
            **self.parameters,
        )

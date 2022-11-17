import pycord

bot = pycord.Bot(intents=pycord.Intents.all(), shards=6)


@bot.listen('on_guild_create')
async def on_ready(guild: pycord.Guild) -> None:
    print(f'  In Guild: {guild.name}')


bot.cluster('token', 2)

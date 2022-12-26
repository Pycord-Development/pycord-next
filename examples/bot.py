import pycord

bot = pycord.Bot(intents=pycord.Intents.all())


@bot.listen('on_guild_available')
async def on_ready(guild: pycord.Guild) -> None:
    print(f'  In Guild: {guild.name}')


bot.run('token')

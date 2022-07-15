import pycord

# a discord bot connecting to the gateway with 1 shard and an intent number of 0
bot = pycord.Bot(0, level='DEBUG')

bot.run('token')

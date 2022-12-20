import pycord

# start the bot with no intents, and with default config
bot = pycord.Bot(intents=pycord.Intents())

# the guild id to deploy on. Often used for developing to
# avoid having to wait the extraneous amount of time Discord has for global
# commands
GUILD_ID: int = 0

# make a chat input command which
# is named favorite and that displays
# an autocompleted list of animes to pick from
@bot.command(
  'favorite',
  pycord.ApplicationCommand,
  type=pycord.ApplicationCommandType.CHAT_INPUT,
  guild_id=GUILD_ID,
)
# make a function for what to do once the user 
# has completed their input.
# this has the option anime, displayed as a Parameter,
# which is parsed by Pycord to give you the information the user gave.
async def favorite(
  inter,
  anime: int = pycord.Option(
    # The type of input the user will put,
    # for this example it's string to support autocomplete.
    pycord.ApplicationCommandOptionType.STRING
    # The name of this option,
    # can be set to anything but
    # try to keep it short
    'anime',
    # The description for this option,
    # this is a longer version of name displaying
    # more detail and technicalities
    'Your favorite Anime Show',
    # this just sets it so the user cannot procede without
    # entering this option
    required=True,
    # enables autocomplete on Discord's side
    autocomplete=True,
    # these are the choices the user can pick.
    # the first value is the name, which is what
    # the user will see. The second is the value, which is what
    # you, or the bot, will see.
    choices=[
      CommandChoice('Attack on Titan', 1),
      CommandChoice('JoJo\'s Bizzare Adventure', 2),
      CommandChoice('Cowboy Bebop', 3),
      CommandChoice('Hunter x Hunter', 4),
      CommandChoice('Spy x Family', 5)
    ]
  )
):
  # checks the value of the int
  # and if it matches up to an anime,
  # it responds with a custom response.
  if anime == 1:
    await inter.resp.send('It seems like you like Attack on Titan, Nice!')
  elif anime == 2:
    await inter.resp.send('おにいちゃんありがとう. You like JoJo\'s Bizzare Adventure. Nice!')
  elif anime == 3:
    await inter.resp.send('良い！あなたはカウボーイビバップが好きです')
  elif anime == 4:
    await inter.resp.send('I ran out of responses... Well anyway, you like Hunter x Hunter which is Nice!')
  elif anime == 5:
    await inter.resp.send('I have a friend which really likes this anime, it\'s good seeing you like it too. Of course, Spy x Family!')

# run the bot with the token token.
# PLEASE REMEMBER TO CHANGE!
bot.run('token')

import pycord

# initiate a bot with 0 intents
bot = pycord.Bot(intents=pycord.Intents())

# create a house to store our components
house = pycord.House()

# add a button to our house
# as well as add a callback for when its interacted with
@house.button(pycord.ButtonStyle.GREEN, 'yes')
async def yes_button(inter: pycord.Interaction) -> None:
    await inter.resp.send('you said yes!')


# add a "no" button in direct reply to
# our "yes" button
# responds the same as yes but with a touch of no
@house.button(pycord.ButtonStyle.RED, 'no')
async def no_button(inter: pycord.Interaction) -> None:
    await inter.resp.send('you said no :(')


# listen for the on_message event
@bot.listen('on_message')
async def on_message(message: pycord.Message) -> None:
    # check if the content in this message aligns
    # with the wanted content of our command
    if message.content == '!!yesorno':
        # send the house singularly
        # if you want to send multiple, just do houses= and set the value as a list
        await message.channel.send('Heres your house mate', house=house)


# run the bot with the token.
# PLEASE REMEMBER TO CHANGE!
bot.run('token')

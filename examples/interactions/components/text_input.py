import pycord
from pycord.components import text_input

# initiate a bot with 0 intents
bot = pycord.Bot(intents=pycord.Intents())

# make a modal which holds our text inputs
favorite_friend_modal = text_input.Modal("Who's your favorite friend?")
# add a text input into this modal
favorite_friend_modal.add_text_input(
    # instantiate a TextInput class
    text_input.TextInput(
        # the name of the text input
        # in this case "Friend Name"
        'Friend Name',
        # should this be styled as a paragraph
        # or shortened? In this case short since it's only names
        pycord.TextInputStyle.SHORT,
        # makes this TextInput required to proceed
        required=True,
        # the placeholder (or example) value set
        placeholder='Michael.. Bob.. Emre..',
    )
)


# a function which runs every time
# a favorite_friend_modal is finished
@favorite_friend_modal.on_call
async def on_favorite_friend_call(inter: pycord.Interaction, name: str) -> None:
    # sends the friends name in chat
    await inter.resp.send(f"{inter.user.name}'s favorite friend is {name}!")


# create an app command to send the modal in
@bot.command(
    # names the app command "favorite_friend"
    'favorite_friend',
    # sets the command type to Application
    pycord.ApplicationCommand,
    # specifies this should be a chat input (slash) command
    type=pycord.ApplicationCommandType.CHAT_INPUT,
    # the command description
    description='Describe your favorite friend within a modal',
    # a test guild to append this command to
    guild_id=None,
)
async def favorite_friend(inter: pycord.Interaction) -> None:
    # send the modal to the user
    await inter.resp.send_modal(modal=favorite_friend_modal)


# run the bot with the token
# PLEASE REMEMBER TO CHANGE!
bot.run('token')

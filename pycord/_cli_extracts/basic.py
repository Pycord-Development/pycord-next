BOT_EXTRACT = """
import pycord

# PLEASE CHANGE THE INTENTS TO ONLY THE ONES NECESSARY!
bot = pycord.Bot(intents=pycord.Intents.all())

@bot.listen()
async def on_ready(_: pycord.Ready) -> None:
    print(f"Ready as {bot.user.name}#{bot.user.discriminator}!")
"""

GEAR_EXTRACT = """
from typing import Annotated

from pycord import Context, Option
from pycord.ext import gears

gear = gears.Gear('my_gear')

@gear.command()
async def echo(
    ctx: Context,
    bespoke: Annotated[str, Option(required=True, description="The text to echo")]
) -> None:
    "\""Echos any input given by the user""\"

    await ctx.send(bespoke)
"""

PYPROJECT = """
[tool.pycord]
# the edition of Pycord CLI Config to use.
edition = "2023"
# whether to load dotenv or not
# must have python-dotenv installed.
# pip install python-dotenv
# if false uses TOKEN variable in bot.py
load_env = true
# the source directory of your bot
src = "src"
# the gears directory of your bot
gears = "src/gears"

[tool.pycord.cluster]
# whether clustering is disabled or not
# should only be enabled for *massive* bots.
enabled = false
"""

<div align='center'>
    <br />
    <p>
        <a href="https://github.com/Pycord-Development/pycord-v3"><img src="https://raw.githubusercontent.com/Pycord-Development/pycord-v3/main/docs/assets/pycord-v3.png" width="546" alt="Pycord v3" /></a>
    </p>
    <p align='center'>
     <b>Empowering developers to build the next generation of Python Discord bots.</b>
    </p>
    <br />
    <p>
        <a href="https://discord.gg/pycord"><img src="https://img.shields.io/discord/881207955029110855?color=5865F2&logo=discord&logoColor=white" alt="discord"> </a>
        <a href="https://pypi.org/project/py-cord"><img src="https://img.shields.io/pypi/v/py-cord?label=pip" alt="pip version"> </a>
        <a href="https://pypi.org/project/py-cord"><img src="https://static.pepy.tech/personalized-badge/py-cord?period=total&units=abbreviation&left_color=grey&right_color=green&left_text=downloads" alt="pip downloads"> </a>
    </p>
</div>

## Introduction

**WARNING: Pycord v3 is pre-alpha, and is highly unstable. We suggest waiting for a alpha, beta, or release candidate before fully migrating.**

Welcome! This is the repository of the shiny new Pycord v3.
Please remember Pycord v3 is still in pre-alpha and anything can change at any time.

The goal of Pycord v3 is to create a more modern Discord library for development of bots in Python.
This comes at the expense of stripping Pycord v2 of many of its either hard to implement, or hard to justify aspects.

Systems like Views (components,) Gears (cogs,) and Commands, have been built from the ground up to provide better systems
for creating Discord bots in Python.

Because of this, many breaking changes have occured. Moreover, the entire library has been rewritten from the ground up
to provide a better internal to take care of. Want to implement your own cache? You can do it! Want to use HTTP-based Interactions, sure!

The old v2 core would've made this nearly impossible (with caching being non-replaceable, and interactions only receivable from the Gateway.)

## Inspiration

Pycord v3 takes some inspiration from some places to try and form an easy to use yet non-limiting library.
Firstly, we take inspiration from Pycord v2 and discord.py for parts of the user parts of the library.
These are mostly parts which obviously don't need changing, like naming, or other such.

Next, we take inspiration from hikari and the hikari ecosystem.
This is for parts of the library like customization, logging, components, gears, etc.
What we try to do differently from hikari is try to provide a higher-level API, and also try to provide
both an easier to use experience and more efficient experience.

Finally, we take some inspiration from some JavaScript libraries for our CLI.
These libraries are the inspiration for the Pycord v3 CLI, and will be a blockpoint for new Pycord bots.

## Example

Example of usage of many of Discord's biggest features.

```py
import pycord

bot = pycord.Bot(pycord.Intents())

# listen for when the bot becomes ready
@bot.listen(pycord.Ready)
async def on_ready() -> None:
    print('Bot is ready!')

# give a high five to a user
@bot.command()
async def highfive(ctx: pycord.Context) -> None:
    # send a response to the command
    await ctx.send(':raised_hand: High Five!')

# this is only for certain things, which we allow the builder api for
view = pycord.View().url_button('Google it!', 'https://google.com')

# a command which sends a button to go to Google.
@bot.command()
async def google(ctx: pycord.Context) -> None:
    iview = view()
    await ctx.send('Just go to Google!', view=iview)

# REMEMBER TO CHANGE THIS!
bot.run('token')
```

## Breaking Changes

- Cogs

    Restructured into Gears.

    Example of Gears:
        
    ```py
        from pycord.ext import gears

        gear = gears.Gear(__name__, BaseContext())

        # somewhere else...
        gear.attach(bot)
    ```
- Commands

    Restructured to provide a better command experience.

    Example of the new command system:
        
    ```py
        @bot.command()
        async def push(ctx: pycord.Context, user: pycord.User) -> None:
            await ctx.send(f'{ctx.user.mention} pushed {user.mention}!')
    ```

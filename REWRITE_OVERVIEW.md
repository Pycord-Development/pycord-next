# Rewrite Overview

Complete overview of every breaking change
made in v3, and why we made them.

## Namespace

By far one of the smallest yet most significant
changes is our namespace.
While v2 used to have the discord namespace
for v3 to signify we're not a fork anymore
we changed it to pycord.

So instead of `import discord` its just
`import pycord` now.

## Generalized Commands

In v3, commands have been restructured
into one system to allow the easy creation
of new ones.

Instead of having `bot.slash_command` and the other types
like in v2, you instead use our one decorator `bot.command`.

Expansibility has been made a priority
for v3, so we also made Commands easy to customize.
Command creators provide a `cls` field to
show which Command class they want to use.
This is required and is not set to any default 

An example Slash Command could be the following:

```py
import pycord

bot = pycord.Bot(...)

@bot.command('echo', pycord.ApplicationCommand, description='Command to echo a message')
async def echo(inter: pycord.Interaction, msg: str = pycord.Option(name='message', description='The message to echo')):
   await inter.resp.send(msg)

bot.run(...)
```

## Extensible Cache

Caching has been rebuilt to allow
higher levels of extensibility.

Do you want to cache on redis? Now you can!
It's extremely easy, just subclass our
Store class and rebuild it for your cacher.

## Extensions

### Cogs

Cogs have been completely reformed from the
ground up to build a brand new and better
experience.

To show that difference, we have renamed Cogs
to Gears, also because it's particularly a better name.

- Basic Cog with Slash Command
  ```py
     from discord.cogs import Cog
     from discord.commands import slash_command

     class MyCog(Cog):
        @slash_command
        async def dunce(self) -> None:
           ...
   ```

- Basic Gear with Slash Command
  ```py
     import pycord
     from pycord.ext.gears import Gear

     gear = Gear(__name__)

     @gear.command('dunce', pycord.ApplicationCommand, type=1, description='duncy command')
     async def dunce(inter: pycord.Interaction) -> None:
        ...
  ```

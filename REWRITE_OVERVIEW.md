# The Pycord Rewrite

v3 aims at making an interface objectively easier to use, faster, and more intuitive than v2.
To do this we have elected that breaking changes in any degree are tolerated.

This means, that with v3 we did not add constraints to differences in UI, or other such.
That means that v3 will feel like a fundamentally different library as compared to v2.
Do not expect v3 to be a drop-in replacement for v2. You will *most likely* have to rewrite
the majority of your bot-facing code.

We do not have all of these "breaking changes" documented or covered, primarily because they
aren't changes in their own right, they are a new way to do it. V3 is a rewrite of v2, so we
do not have any obligation to hold back on necessary breaking changes, especially since we follow
SemVer.


This document will justify and showcase many of these major breaking changes and show
why they were made. So let's get started.


### Bots

Firstly is just your bot. Pycord v3 removes `commands.Bot` (we don't support prefix commands anymore,)
and `Client` for just a single `Bot` class abstracting all of these things.

We try to make the Bot class as extensible as possible so as to not force you to sub-class, but if needed,
The opportunity is always there.

`.run` has been removed from Bots, and bots must now have to be started manually.
This forces developers to grapple with async i/o and makes it easier to do things like
database connections before your bot starts.


```py
# decorator for identifying commands, or parent commands.
# sub commands should use a sort of `parent.command` design.

@command()
async def echo(
   cx: Context,
   input: Annotated[str, Option(description="What do you want me to say?")]
):
   await cx.say(input)


# events now use classes instead of strings.
# this is a much more extensible system and makes it easier for
# developers to make extensions

@listen()
async def on_ready(event: Ready):
   print(f"I'm online and logged into {event.user.name}!")


async def main():
   bot = Bot(
      token='token',
      guild_ids=[...],
      commands=[await echo.build()]
   )

   await bot.start()


if __name__ == "__main__":
   asyncio.run(main())
```

### Cogs are Gone.

As of version 3, Pycord will no longer be supporting Cogs in their current design.
We will still support grouping your commands and listeners in separate files, just with a
smarter and less object-oriented way.


```py
async def setup():
   return [
      cx,
      command,
      listener
   ]
```


# A tiny note

There is still more content on the way! The more v3 develops, the more we'll add here :)
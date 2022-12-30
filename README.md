<div align='center'>
    <br />
    <p>
        <a href="https://github.com/Pycord-Development/pycord-v3"><img src="https://raw.githubusercontent.com/Pycord-Development/pycord-v3/main/docs/assets/pycord-v3.png" width="546" alt="Pycord v3" /></a>
    </p>
    <br />
    <p>
        <a href="https://discord.gg/pycord"><img src="https://img.shields.io/discord/881207955029110855?color=5865F2&logo=discord&logoColor=white" alt="discord"> </a>
        <a href="https://pypi.org/project/py-cord"><img src="https://img.shields.io/pypi/v/py-cord?label=pip" alt="pip version"> </a>
        <a href="https://pypi.org/project/py-cord"><img src="https://static.pepy.tech/personalized-badge/py-cord?period=total&units=abbreviation&left_color=grey&right_color=green&left_text=downloads" alt="pip downloads"> </a>
    </p>
</div>

<p align='center'>
 <b>Make Bots Happen.</b>
</p>

Welcome! This is the repository for the pre-alpha and heavy conception next major
version of Pycord.

## Installation

Pycord v3 is not yet published onto PyPi, so for now you'll have to install via git. To
do this, you should install [git](https://git-scm.com) if not already installed.

An automatic install should look something like

```sh
    pip install -U git+https://github.com/pycord-development/pycord-v3
```

If instead, you wanted to do a manual install (in case of something like development),
you could do the following

```sh
    # Git command
    git clone https://github.com/pycord-development/pycord-v3
    cd pycord-v3

    pip install .
```

## Stability

While we are working and striving for stability throughout v3, it's still quite a new
library so breakages can still happen especially with us still being in a pre-alpha
stage.

## Breaking Changes

v3 is a new **major version** of pycord, meaning breaking changes have occurred.
Although a much larger amount than v2, v3 introduces a new paradigm for Pycord bots and
ensures code quality for developers (of the library.)

Every aspect of v2 has been remade and improved upon to make your development experience
quicker, easier, and mucho gracias. Breaking changes are everywhere, from typings to
Python version increases.

That being said, if you want to move your bot to v3 you'll have to rewrite it. We've
made sure to make the rewriting experience easier though, providing less boilerplate
than v2 and letting you do anything in smaller snippets.

## Making Good Bots Happen

v3 is made to be the best experience for both
developers and users, providing a fast
experience for users and a good interface for that for the developer.

We've adopted a modern interface inspired by
Hikari to form an interface easier, smarter, and objectively better than discord.py.

Instead of following a mix of object-instance paradigm (in this case think of cog-bot)
we're following an instance-only paradigm completely restructuring old features and stripping useless parts from them.
Overall a cleanup of v2, and new better interface.

## Code Example

A small code snippet of a basic Pycord v3 bot.

```py
import pycord

# If you want more interactivity with models and events, you'll want to add more intents
bot = pycord.Bot(intents=pycord.Intents(guilds=True))


@bot.listen('on_guild_available')
async def handle_new_guild(guild: pycord.Guild) -> None:
    print(f'  In Guild: {guild.name}')


bot.run('token')
```

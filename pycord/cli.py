# cython: language_level=3
# Copyright (c) 2021-present Pycord Development
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

import tomllib

from ._cli_extracts import basic
from .bot import Bot
from .ext.gears.gear import Gear

pyproject_toml = Path('pyproject.toml')

if pyproject_toml.exists():
    pyproject = tomllib.loads(pyproject_toml.read_text('utf-8'))
    tool: dict[str, Any] = pyproject['tool']['pycord']
else:
    pyproject = None


def new():
    if pyproject is not None:
        raise ValueError('pyproject.toml must not exist')

    Path('gears').mkdir()
    Path('bot.py').write_text(basic.BOT_EXTRACT)
    Path('gears/example_gear.py').write_text(basic.GEAR_EXTRACT)
    Path('pyproject.toml').write_text(basic.PYPROJECT)

    print('✨ Successfully setup your new Pycord Bot! ✨', file=sys.stderr)


def verify_paths(*paths: Path) -> None:
    for path in paths:
        if not path.exists():
            raise ValueError(f'Path {path.name} does not exist')


def run():
    if not pyproject:
        raise ValueError('pyproject.toml must exist')

    bot_var = tool.get('bot_var', 'bot')
    gears = Path('gears')
    bot_py = Path('bot.py')

    verify_paths(bot_py)

    bot_spec = importlib.util.spec_from_file_location('bot', bot_py.absolute())
    bot_mod = importlib.util.module_from_spec(bot_spec)
    sys.modules['bot'] = bot_mod
    bot_spec.loader.exec_module(bot_mod)
    bot = getattr(bot_mod, bot_var)

    assert isinstance(
        bot, Bot
    ), f'{bot_var} must be of type Bot, or changed to another variable name.'

    loaded_gears = ''

    if gears.exists():
        for gear in gears.glob('*'):
            path = gear.absolute()

            name = gear.name.removesuffix('.py')
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None:
                continue

            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)

            for attr in dir(mod):
                attr = getattr(mod, attr)
                if isinstance(attr, Gear):
                    attr.attach(bot)
                    loaded_gears += f'\n        {attr.name}'

    # TODO: beautify!
    print(
        f'    Finished bot initialization. Loaded gears:{loaded_gears}', file=sys.stderr
    )

    if tool.get('load_env', False) is True:
        try:
            import dotenv
        except ImportError:
            raise ValueError(
                'dotenv is not installed on your system. Please run pip install -U dotenv or other such command to get dotenv installed.'
            )
        dotenv.load_dotenv(Path('.env').absolute())

        token = os.environ['TOKEN']
    else:
        token = bot_mod.TOKEN

    if tool['cluster']['enabled'] is True:
        bot.cluster(
            token,
            tool['cluster']['clusters'],
            tool['cluster']['amount'],
            tool['cluster']['managers'],
        )
    else:
        bot.run(token)

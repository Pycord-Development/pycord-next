# MIT License

# Copyright (c) 2021-present Pycord Development

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from glob import glob

import mypyc.build
import setuptools

__version__ = "3.0.0"

requirements = []
with open("requirements/_.txt") as f:
    requirements = f.read().splitlines()

packages: list[str] = []


for fn in os.scandir("pycord"):
    if fn.is_dir():
        packages.append(f.name)


def get_extra_requirements() -> dict[str, list[str]]:
    extra_requirements: dict[str, list[str]] = {}
    for fn in os.scandir("requirements"):
        if fn.is_file() and fn.name != "required.txt":
            with open(fn) as f:
                extra_requirements[fn.name.split(".")[0]] = f.read().splitlines()
    return extra_requirements


mods = glob("pycord/**/*.py", recursive=True)
# excluded modules
for m in mods:
    if "missing.py" in m:
        mods.remove(m)
    elif "event_manager.py" in m:
        mods.remove(m)
    elif "flags.py" in m:
        mods.remove(m)


setuptools.setup(
    name="py-cord",
    version=__version__,
    packages=packages,
    package_data={
        "pycord": ["panes/*.txt", "bin/*.dll"],
    },
    project_urls={
        "Documentation": "https://docs.pycord.dev",
        "Issue Tracker": "https://github.com/pycord/pycord-v3/issues",
        "Pull Request Tracker": "https://github.com/pycord/pycord-v3/pulls",
    },
    url="https://github.com/pycord/pycord-v3",
    license="MIT",
    author="Pycord Development",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require=get_extra_requirements(),
    description="A modern Discord API wrapper for Python",
    python_requires=">=3.11",
    # mypyc specific
    # TODO!
    # py_modules=[],
    # ext_modules=mypyc.build.mypycify(
    #     [
    #         "--ignore-missing-imports",
    #         *mods
    #     ]
    # ),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)

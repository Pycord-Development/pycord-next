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
import setuptools

__version__ = '3.0.0'

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

packages = [
    'pycord',
    'pycord.ui',
    'pycord.types',
    'pycord.api',
    'pycord.api.execution',
    'pycord.gateway',
    'pycord.commands',
    'pycord.commands.application',
    'pycord.api.routers',
    'pycord.ext',
    'pycord.ext.gears',
    'pycord.ext.pager',
]

extra_requires = {
    'speed': [
        'msgspec~=0.9.1',  # Faster alternative to the normal json module.
        'aiodns~=3.0',  # included in aiohttp speed.
        'Brotli~=1.0.9',  # included in aiohttp speed.
        'ciso8601~=2.2.0',  # Faster datetime parsing.
    ],
    'docs': [
        'sphinx==5.3.0',
        'sphinx-hoverxref~=1.0.1',
    ],
}

setuptools.setup(
    name='py-cord',
    version=__version__,
    packages=packages,
    package_data={
        'pycord': ['banner.txt', 'ibanner.txt', 'bin/*.dll'],
    },
    project_urls={
        'Documentation': 'https://docs.pycord.dev',
        'Issue Tracker': 'https://github.com/pycord/pycord-v3/issues',
        'Pull Request Tracker': 'https://github.com/pycord/pycord-v3/pulls',
    },
    url='https://github.com/pycord/pycord-v3',
    license='MIT',
    author='Pycord Development',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    extras_require=extra_requires,
    description="Python's Intuitive Discord API Wrapper",
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: AsyncIO',
        'Framework :: aiohttp',
        'Topic :: Communications :: Chat',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)

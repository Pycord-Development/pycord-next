# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Pycord'

copyright = '2021-present, Pycord Development'
author = 'Pycord Development'
release = '3.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))

extensions = [
    'resourcelinks',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_member_order = 'bysource'
autodoc_typehints = 'none'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

resource_links = {
    'guide': 'https://guide.pycord.dev',
    'repository': 'https://github.com/pycord-development/pycord-v3',
}

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    'py': ('https://docs.python.org/3', None),
    'aio': ('https://docs.aiohttp.org/en/stable/', None),
}

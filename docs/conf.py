# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Pycord"

copyright = "2021-present, Pycord Development"
author = "Pycord Development"
release = "3.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))

extensions = [
    "resourcelinks",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_member_order = "bysource"
autodoc_typehints = "none"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
html_static_path = ["_static"]

html_logo = "https://raw.githubusercontent.com/Pycord-Development/pycord-v3/main/docs/assets/pycord-v3.png"

# Any option(s) added to your certain theme.
# in this case, Pydata
html_theme_options = {
    "footer_items": ["copyright", "sphinx-version"],
}

html_sidebars = {"**": ["sidebar-nav-bs"]}

resource_links = {
    "guide": "https://guide.pycord.dev",
    "repository": "https://github.com/pycord-development/pycord-v3",
}

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
}

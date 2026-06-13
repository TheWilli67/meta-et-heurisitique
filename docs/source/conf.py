import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'Couverture Maximale sous Contrainte de Budget'
copyright = '2025-2026, William HERTRICH, Théo PLUVINAGE, Christophe GRILLET-AUBERT, Ludovic URBES'
author = 'William HERTRICH · Théo PLUVINAGE · Christophe GRILLET-AUBERT · Ludovic URBES'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = []
language = 'fr'

html_theme = 'furo'
html_static_path = []
html_title = 'Couverture Maximale sous Contrainte de Budget'
html_short_title = 'CouvertureMax'

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#1a6fa8",
        "color-brand-content": "#1a6fa8",
        "color-admonition-background": "rgba(26, 111, 168, 0.05)",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5dade2",
        "color-brand-content": "#5dade2",
    },
}

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': True,
    'special-members': '__init__',
}

napoleon_google_docstring = False
napoleon_numpy_docstring = False
napoleon_use_admonition_for_notes = True

mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'

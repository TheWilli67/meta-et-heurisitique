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

html_theme = 'sphinx_rtd_theme'
html_static_path = []
html_title = 'Couverture Maximale — Budget'
html_short_title = 'CouvertureMax'

html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'titles_only': False,
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

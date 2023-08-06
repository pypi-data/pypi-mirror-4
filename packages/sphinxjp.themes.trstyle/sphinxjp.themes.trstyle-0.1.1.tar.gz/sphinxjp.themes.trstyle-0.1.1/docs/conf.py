# -*- coding: utf-8 -*-
#
# -- General configuration -----------------------------------------------------

source_suffix = '.rst'
master_doc = 'index'

project = u'sphinx theme for TriAx Corp style'
copyright = u'2011, triax.jp'

# The short X.Y version.
version = '0.1.0'
# The full version, including alpha/beta/rc tags.
release = '0.1.0'

# -- Options for HTML output ---------------------------------------------------

extensions = ['sphinx.ext.todo', 'sphinxjp.themecore']
html_theme = 'trstyle'

html_theme_options = {
    'rightsidebar': False,
}

[extensions]
todo_include_todos = True

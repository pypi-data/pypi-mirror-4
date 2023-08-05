# -*- coding: utf-8 -*-
#
# fx documentation build configuration file.
import sys, os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, PROJECT_DIR)
import fx

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest'
]

source_suffix = '.rst'

master_doc = 'index'

project = u'fx'
copyright = u'2012, Philip Xu'

version = '%d.%d' % fx.__version__
release = fx.VERSION

exclude_patterns = ['_build']

pygments_style = 'sphinx'

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    html_theme = 'default'
else:
    html_theme = 'pyramid'

htmlhelp_basename = 'fxdoc'

latex_documents = [
  ('index', 'fx.tex', u'fx Documentation',
   u'Philip Xu', 'manual'),
]

man_pages = [
    ('index', 'fx', u'fx Documentation',
     [u'Philip Xu'], 3)
]

texinfo_documents = [
  ('index', 'fx', u'fx Documentation',
   u'Philip Xu', 'fx', fx.__doc__,
   'Miscellaneous'),
]

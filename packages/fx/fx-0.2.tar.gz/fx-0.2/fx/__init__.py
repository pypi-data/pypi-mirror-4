# -*- coding: utf-8 -*-
# Copyright 2012, Philip Xu <pyx@xrefactor.com>
# License: BSD New, see LICENSE for details.
"""fx - a functional programming approach"""

__all__ = ['Function', 'compose', 'flip']

__version__ = (0, 2)
__release__ = ''

VERSION = '%d.%d' % __version__ + __release__

from fx.function import Function
from fx.utils import compose, flip

# alias for less typing
f = Function

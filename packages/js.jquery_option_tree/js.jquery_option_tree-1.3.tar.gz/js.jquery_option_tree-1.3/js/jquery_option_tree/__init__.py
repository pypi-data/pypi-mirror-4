# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library(
    'jquery_option_tree',
    'resources'
)

jquery_option_tree = Resource(
    library,
    'jquery.optionTree.js',
    minified='jquery.optionTree.min.js',
    depends=[jquery, ]
)

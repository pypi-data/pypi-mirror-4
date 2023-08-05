# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library(
    'jquery.maskedinput',
    'resources')

jquery_maskedinput = Resource(
    library,
    'jquery.maskedinput.js',
    minified='jquery.maskedinput.min.js',
    depends=[jquery, ])

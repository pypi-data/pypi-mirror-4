# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library(
    'jquery-maskmoney',
    'resources')
jquery_maskmoney = Resource(
    library,
    'jquery.maskmoney.js',
    minified='jquery.maskmoney.min.js',
    depends=[jquery, ])

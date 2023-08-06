# -*- coding: utf-8 -*-

"""
Created on 2013-03-05
:author: Andreas Kaiser (disko)
"""

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource
from js.bootstrap import bootstrap_js
from js.jquery import jquery


library = Library('bootstrap_timepicker', 'resources')

bootstrap_timepicker_js = Resource(
    library,
    'bootstrap-timepicker.js',
    minified='bootstrap-timepicker.min.js',
    depends=[jquery, bootstrap_js, ])
bootstrap_timepicker_css = Resource(
    library,
    'bootstrap-timepicker.css',
    minified='bootstrap-timepicker.min.css')

bootstrap_timepicker = Group([
    bootstrap_timepicker_js, bootstrap_timepicker_css
])

# -*- coding: utf-8 -*-

"""
Created on 2013-02-23
:author: Andreas Kaiser (disko)
"""

from fanstatic import Library
from fanstatic import Resource

library = Library(
    'javascript_templates',
    'resources'
    )

tmpl = Resource(
    library,
    'tmpl.js',
    minified='tmpl.min.js'
    )

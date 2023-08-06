from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

from kotti.fanstatic import view_needed
from js.deform_bootstrap import deform_bootstrap_js

library = Library('kotti_contentpreview', 'static')
css = Resource(
    library,
    'kotti_contentpreview.css',
    minified='kotti_contentpreview.min.css',
    bottom=True
)
js = Resource(
    library,
    'kotti_contentpreview.js',
    minified='kotti_contentpreview.min.js',
    depends=[deform_bootstrap_js],
    bottom=True
)
view_needed.add(Group([css, js, ]))

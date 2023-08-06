from __future__ import absolute_import

from fanstatic.core import render_css
from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library('kotti_tagcloud', 'static')


def lte_ie_renderer(url):
    inner = render_css(url)
    return "<!--[if IE]>{0}<![endif]-->".format(inner)


css = Resource(
    library,
    'css/style.css',
    minified='css/style.min.css'
)

js = Resource(
    library,
    'js/script.js',
    minified='js/script.min.js',
    depends=[jquery, ]
)

tagcanvas = Resource(
    library,
    'js/jquery.tagcanvas.js',
    minified='js/jquery.tagcanvas.min.js',
    depends=[jquery, ]
)


excanvas = Resource(
    library,
    'js/excanvas.js',
    minified='js/excanvas.min.js',
    renderer=lte_ie_renderer
)

kotti_tagcloud = Group([css, excanvas, tagcanvas, js, ])

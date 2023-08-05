# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library(
    'mediaelement.js',
    'resources'
)

mediaelement_js = Resource(
    library,
    'mediaelement.js',
    minified="mediaelement.min.js"
)
mediaelementplayer_css = Resource(
    library,
    'mediaelementplayer.css',
    minified="mediaelementplayer.min.css"
)
mediaelementplayer_js = Resource(
    library,
    'mediaelementplayer.js',
    minified="mediaelementplayer.min.js",
    depends=[jquery, ]
)
mediaelementandplayer = Resource(
    library,
    'mediaelement-and-player.js',
    minified="mediaelement-and-player.min.js",
    depends=[jquery, mediaelementplayer_css, ]
)

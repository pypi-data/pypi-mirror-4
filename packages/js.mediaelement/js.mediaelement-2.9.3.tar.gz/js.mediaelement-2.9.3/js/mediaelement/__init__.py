# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource

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
    minified="mediaelementplayer.min.js"
)
mediaelementandplayer = Resource(
    library,
    'mediaelement-and-player.js',
    minified="mediaelement-and-player.min.js",
    depends=[mediaelementplayer_css, ]
)

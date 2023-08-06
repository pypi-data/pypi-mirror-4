# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource
from js.angular import angular


library = Library(
    'ngupload',
    'resources'
    )
upload = Resource(
    library,
    'upload.js',
    minified='upload.min.js',
    depends=[angular]
    )

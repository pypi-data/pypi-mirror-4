from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery
from js.jqueryui import ui_core

library = Library('jquery.dynatree.js', 'resources')

dynatree = Resource(
    library,
    'jquery.dynatree.js',
    minified='jquery.dynatree.min.js',
    depends=[jquery, ui_core])

dynatree_skin = Resource(
    library,
    'skin/ui.dynatree.css',
    minified='skin/ui.dynatree.min.css')

dynatree_skin_vista = Resource(
    library,
    'skin-vista/ui.dynatree.css',
    minified='skin-vista/ui.dynatree.min.css')

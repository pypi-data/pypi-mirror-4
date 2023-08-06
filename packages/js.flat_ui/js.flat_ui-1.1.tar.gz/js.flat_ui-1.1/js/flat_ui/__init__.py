from fanstatic import Library, Resource
from js.bootstrap import bootstrap

library = Library('flat_ui', 'resources')

flat_ui                       = Resource(library, 'css/flat-ui.css',
                                         minified='css/flat-ui.min.css',
                                         depends=[bootstrap])

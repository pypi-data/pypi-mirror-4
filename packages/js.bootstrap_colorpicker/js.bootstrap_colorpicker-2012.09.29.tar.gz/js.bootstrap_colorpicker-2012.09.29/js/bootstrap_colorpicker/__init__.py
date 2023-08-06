from fanstatic import Library, Resource, Group
from js.bootstrap import bootstrap_css, bootstrap_js

library = Library('bootstrap-colorpicker', 'resources')

bootstrap_colorpicker_css = Resource(library, 'css/colorpicker.css',
                                    minified='css/colorpicker.min.css',
                                    depends=[bootstrap_css])
bootstrap_colorpicker_js = Resource(library, 'js/bootstrap-colorpicker.js',
                                   minified='js/bootstrap-colorpicker.min.js',
                                   depends=[bootstrap_js])

bootstrap_colorpicker = Group([bootstrap_colorpicker_css, bootstrap_colorpicker_js])
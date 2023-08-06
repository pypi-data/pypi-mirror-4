from fanstatic import Library, Resource, Group
from js.bootstrap import bootstrap_css, bootstrap_js

library = Library('bootstrap-datepicker', 'resources')

bootstrap_datepicker_css = Resource(library, 'css/datepicker.css',
                                    minified='css/datepicker.min.css',
                                    depends=[bootstrap_css])
bootstrap_datepicker_js = Resource(library, 'js/bootstrap-datepicker.js',
                                   minified='js/bootstrap-datepicker.min.js',
                                   depends=[bootstrap_js])

bootstrap_datepicker = Group([bootstrap_datepicker_css, bootstrap_datepicker_js])
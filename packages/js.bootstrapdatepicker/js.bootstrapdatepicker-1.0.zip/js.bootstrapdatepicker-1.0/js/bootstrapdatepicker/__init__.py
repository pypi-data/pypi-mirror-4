from fanstatic import Library, Resource, Group
from js.bootstrap import bootstrap_css, bootstrap_js

library = Library('bootstrapdatepicker', 'resources')

bootstrapdatepicker_css = Resource(library, 'css/bootstrap-datepicker.css',
                         depends=[bootstrap_css])

bootstrapdatepicker_js = Resource(library, 'js/bootstrap-datepicker.js',
                        depends=[bootstrap_js])

bootstrapdatepicker = Group([bootstrapdatepicker_css, bootstrapdatepicker_js])

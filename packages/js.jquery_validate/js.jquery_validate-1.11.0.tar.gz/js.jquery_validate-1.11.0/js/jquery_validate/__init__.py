from fanstatic import Library, Resource, Group
from js.jquery import jquery

library = Library('jquery-validate', 'resources')

jquery_validate = Resource(library, 'jquery.validate.js',
                           minified='jquery.validate.min.js',
                           depends=[jquery])

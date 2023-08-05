import fanstatic
import js.jquery

library = fanstatic.Library('ember', 'resources')

ember = fanstatic.Resource(library, 'ember.js', minified='ember.min.js',
                 depends=[js.jquery.jquery])

from fanstatic import Library, Resource

library = Library('raven', 'resources')

raven = Resource(library, 'raven.js', minified='raven.min.js')

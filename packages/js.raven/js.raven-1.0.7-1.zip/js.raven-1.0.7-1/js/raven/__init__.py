from fanstatic import Library, Resource
import js.json2

library = Library('raven', 'resources')

raven = Resource(library, 'raven.js', minified='raven.min.js',
        depends=[js.json2.json2])

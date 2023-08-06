from fanstatic import Library, Resource
import js.jquery

library = Library('jstorage', 'resources')

jstorage = Resource(library, 'jstorage.js', minified='jstorage.min.js',
        depends=[js.jquery.jquery])

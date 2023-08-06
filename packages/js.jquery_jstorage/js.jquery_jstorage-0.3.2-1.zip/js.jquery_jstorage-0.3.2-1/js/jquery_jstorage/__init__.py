from fanstatic import Library, Resource
import js.jquery
import js.json2

library = Library('jstorage', 'resources')

jstorage = Resource(library, 'jstorage.js', minified='jstorage.min.js',
        depends=[js.jquery.jquery, js.json2.json2])

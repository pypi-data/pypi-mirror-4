from js.jquery import jquery

from fanstatic import Library, Resource


library = Library('jquery-json', 'resources')

jquery_json = Resource(library, 'jquery.json.js',
    minified='jquery.json.min.js',
    depends=[jquery])

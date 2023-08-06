from fanstatic import Library, Resource
import js.jquery

library = Library('jquery.socialshareprivacy', 'resources')

css = Resource(library, 'socialshareprivacy.css')

socialshareprivacy = Resource(library, 'jquery.socialshareprivacy.js',
                              minified='jquery.socialshareprivacy.min.js',
                              depends=[js.jquery.jquery, css])

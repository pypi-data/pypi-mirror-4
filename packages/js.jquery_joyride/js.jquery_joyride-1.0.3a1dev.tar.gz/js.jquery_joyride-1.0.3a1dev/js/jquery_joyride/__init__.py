from fanstatic import Library, Resource
import js.jquery

library = Library('joyride', 'resources')

css = Resource(library, 'joyride-dadb4d120f.css')

joyride = Resource(library, 'jquery.joyride-dadb4d120f.js',
                              minified='jquery.joyride.min-dadb4d120f.js',
                              depends=[js.jquery.jquery, css])

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')

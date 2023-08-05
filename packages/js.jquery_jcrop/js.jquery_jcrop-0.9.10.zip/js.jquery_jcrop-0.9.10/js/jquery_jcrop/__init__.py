from fanstatic import Library, Resource, Group
from js.jquery import jquery

library = Library('jcrop', 'resources')

jquery_jcrop_css = Resource(library, 'jquery.Jcrop.css',
                     minified='jquery.Jcrop.min.css')

jquery_color_js = Resource(library, 'jquery.color.js')
jquery_jcrop_js = Resource(library, 'jquery.Jcrop.js',
                    minified='jquery.Jcrop.min.js', depends=[jquery])

jquery_jcrop = Group([jquery_jcrop_css, jquery_jcrop_js])

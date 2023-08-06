from fanstatic import Library, Resource, Group
from js.jquery import jquery

library = Library('jquery-gritter', 'resources')

jquery_gritter_css = Resource(library, 'css/jquery.gritter.css',
                                    minified='css/jquery.gritter.min.css')
jquery_gritter_js = Resource(library, 'js/jquery.gritter.js',
                                   minified='js/jquery.gritter.min.js',
                                   depends=[jquery])

jquery_gritter = Group([jquery_gritter_css, jquery_gritter_js])
from fanstatic import Library, Resource
from js.angular import angular

library = Library('unicode_eastasianwidth', 'resources')

unicode_eastasianwidth          = Resource(library, 'unicode_eastasianwidth.js',
                                           minified='unicode_eastasianwidth.min.js')
angular_unicode_eastasianwidth  = Resource(library, 'angular-unicode_eastasianwidth.js',
                                           minified='angular-unicode_eastasianwidth.min.js',
                                           depends=[angular])

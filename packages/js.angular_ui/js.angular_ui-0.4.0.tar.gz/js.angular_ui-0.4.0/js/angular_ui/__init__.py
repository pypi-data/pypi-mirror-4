from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource
from js.angular import angular

library = Library('angularui', 'resources')

angular_ui_css = Resource(library, 'angular-ui.css',
                          minified='angular-ui.min.css')

angular_ui_js = Resource(library, 'angular-ui.js',
                         minified='angular-ui.min.js',
                         depends=[angular])

angular_ui_ieshiv_js = Resource(library, 'angular-ui-ieshiv.js',
                                minified='angular-ui-ieshiv.min.js',
                                depends=[angular_ui_js])

angular_ui = Group([angular_ui_css, angular_ui_js])
angular_ui_ieshiv = Group([angular_ui_css, angular_ui_ieshiv_js])

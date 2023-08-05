from fanstatic import Library, Resource

library = Library('jquery_ui_touch_punch', 'resources')

touch_punch = Resource(
    library, 'jquery.ui.touch-punch.js',
    minified='jquery.ui.touch-punch.min.js')

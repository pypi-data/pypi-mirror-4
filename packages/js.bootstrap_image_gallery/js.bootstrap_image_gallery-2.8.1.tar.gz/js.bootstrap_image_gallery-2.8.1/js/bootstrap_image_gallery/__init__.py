from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource
from js.bootstrap import bootstrap_js


library = Library('bootstrap_image_gallery', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
loadimage = Resource(
    library,
    'js/load-image.js',
    minified='js/load-image.min.js')

gallery_css = Resource(
    library,
    'css/bootstrap-image-gallery.css',
    minified='css/bootstrap-image-gallery.min.css')

gallery_js = Resource(
    library,
    'js/bootstrap-image-gallery.js',
    minified='js/bootstrap-image-gallery.min.js',
    depends=[loadimage, bootstrap_js])

gallery = Group([gallery_css, gallery_js])

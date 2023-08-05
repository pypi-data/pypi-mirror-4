from fanstatic import Library, Resource, Group
from js.jquery import jquery

library = Library('jquery_datatables', 'resources')

# Define the resources in the library like this.
# For options and examples, see the fanstatic documentation.
# resource1 = Resource(library, 'style.css')

jquery_datatables_css = Resource(
    library,
    'media/css/jquery.dataTables.css'
)

jquery_datatables_js = Resource(
    library, 'media/js/jquery.dataTables.js',
    depends=[jquery],
    minified='media/js/jquery.dataTables.min.js'
)

jquery_datatables = Group(depends=[
        jquery_datatables_css, jquery_datatables_js]
)

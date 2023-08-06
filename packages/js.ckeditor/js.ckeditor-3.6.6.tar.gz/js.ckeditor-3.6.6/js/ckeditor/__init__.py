from fanstatic import Library, Resource

library = Library('ckeditor', 'resources')

ckeditor = Resource(library, 'ckeditor_source.js', minified='ckeditor.js')

try:
    from js.jquery import jquery
    jquery_adapter = Resource(
        library, 'adapters/jquery.js', depends=[ckeditor, jquery])
except ImportError:
    pass

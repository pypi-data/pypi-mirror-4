from fanstatic import Library, Resource

library = Library('howler', 'resources')

howler = Resource(library, 'howler.js', minified='howler.min.js')

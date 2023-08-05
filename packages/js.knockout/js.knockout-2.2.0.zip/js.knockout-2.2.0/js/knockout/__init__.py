import fanstatic

library = fanstatic.Library('knockout', 'resources')

knockout = fanstatic.Resource(
    library,
    'knockout.js',
    minified='knockout.min.js'
)

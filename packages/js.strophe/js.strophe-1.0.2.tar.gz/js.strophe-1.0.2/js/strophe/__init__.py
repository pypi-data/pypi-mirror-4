import fanstatic

library = fanstatic.Library('strophe.js', 'resources')

strophe = fanstatic.Resource(
    library, 'strophe.js', minified='strophe.min.js')

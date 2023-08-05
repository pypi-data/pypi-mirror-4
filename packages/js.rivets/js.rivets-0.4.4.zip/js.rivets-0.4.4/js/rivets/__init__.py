import fanstatic

library = fanstatic.Library('rivets', 'resources')

rivets = fanstatic.Resource(
    library,
    'rivets.js',
    minified='rivets.min.js'
)

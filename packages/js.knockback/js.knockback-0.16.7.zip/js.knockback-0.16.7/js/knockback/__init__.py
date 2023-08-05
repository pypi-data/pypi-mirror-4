import fanstatic
import js.backbone
import js.knockout
import js.underscore


library = fanstatic.Library('knockback', 'resources')

knockback = fanstatic.Resource(
    library,
    'knockback.js',
    minified='knockback.min.js',
    depends=[js.backbone.backbone,
             js.knockout.knockout,
             js.underscore.underscore])

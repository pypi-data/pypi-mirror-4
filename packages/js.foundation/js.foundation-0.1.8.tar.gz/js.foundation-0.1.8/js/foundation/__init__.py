from fanstatic import Library, Resource, Group
from js.jquery import jquery
from js.jquery_cookie import cookie

library = Library('foundation', 'resources')

# 3rd party
modernizr = Resource(library, 'js/modernizr.foundation.js')
placeholder = Resource(library, 'js/jquery.placeholder.js')

# initialize plugins
app = Resource(library, 'js/app.js', depends=[jquery, modernizr], bottom=True)
app.order = 10000  # Push this to the bottom so plugins are all loaded beforehand

# foundation.min.js includes all foundation js along with modernizr and jquery
foundation_js = Resource(library, 'js/foundation.min.js', depends=[jquery, modernizr, app], bottom=True)
foundation_css = Resource(library, 'css/app.css', minified='css/app.min.css')
foundation = Group([foundation_js, foundation_css])

# Foundation
accordion = Resource(library, 'js/jquery.foundation.accordion.js', depends=[jquery, modernizr], bottom=True)
alerts = Resource(library, 'js/jquery.foundation.alerts.js', depends=[jquery], bottom=True)
buttons = Resource(library, 'js/jquery.foundation.buttons.js', depends=[jquery], bottom=True)
clearing = Resource(library, 'js/jquery.foundation.clearing.js', depends=[jquery], bottom=True)
forms = Resource(library, 'js/jquery.foundation.forms.js', depends=[jquery], bottom=True)
joyride = Resource(library, 'js/jquery.foundation.joyride.js', depends=[jquery, modernizr, cookie], bottom=True)
magellan = Resource(library, 'js/jquery.foundation.magellan.js', depends=[jquery], bottom=True)
mediaQueryToggle = Resource(library, 'js/jquery.foundation.mediaQueryToggle.js', depends=[jquery], bottom=True)
navigation = Resource(library, 'js/jquery.foundation.navigation.js', depends=[jquery, modernizr], bottom=True)
orbit = Resource(library, 'js/jquery.foundation.orbit.js', depends=[jquery], bottom=True)
reveal = Resource(library, 'js/jquery.foundation.reveal.js', depends=[jquery], bottom=True)
tabs = Resource(library, 'js/jquery.foundation.tabs.js', depends=[jquery], bottom=True)
tooltips = Resource(library, 'js/jquery.foundation.tooltips.js', depends=[jquery, modernizr], bottom=True)
topbar = Resource(library, 'js/jquery.foundation.topbar.js', depends=[jquery, modernizr], bottom=True)

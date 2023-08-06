import fanstatic

library = fanstatic.Library('smoke', 'resources')

base_css = fanstatic.Resource(
    library, 'smoke.css')

theme_100s = fanstatic.Resource(
    library, 'themes/100s.css', depends=[base_css])

theme_dark = fanstatic.Resource(
    library, 'themes/dark.css', depends=[base_css])

theme_tiger = fanstatic.Resource(
    library, 'themes/tiger.css', depends=[base_css])

css = fanstatic.Slot(library, '.css', default=base_css)

smoke_js = fanstatic.Resource(library, 'smoke.js', minified='smoke.min.js', depends=[css])


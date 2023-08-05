from fanstatic import Library
from fanstatic import Resource
from kotti.fanstatic import NeededGroup
from kotti.fanstatic import edit_needed_js
from kotti.fanstatic import view_needed_js

library = Library('kotti_theme_slate', 'static')
css = Resource(library, 'css/bootstrap.css', minified='css/bootstrap.min.css')

edit_needed = NeededGroup([css, edit_needed_js, ])
view_needed = NeededGroup([css, view_needed_js, ])


def kotti_configure(settings):
    settings['kotti.fanstatic.view_needed'] = 'kotti_theme_slate.view_needed'
    settings['kotti.fanstatic.edit_needed'] = 'kotti_theme_slate.edit_needed'
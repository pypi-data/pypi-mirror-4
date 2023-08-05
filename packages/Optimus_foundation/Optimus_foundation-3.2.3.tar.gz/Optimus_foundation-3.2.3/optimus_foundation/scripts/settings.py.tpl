# -*- coding: utf-8 -*-
"""
Settings file for $PROJECT_NAME
"""
import os

# Uncomment this if you want to add some custom bundles
from webassets import Bundle

DEBUG = True

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

# Common site name and domain to use available in templates
SITE_NAME = '$PROJECT_NAME'
SITE_DOMAIN = 'localhost'

# Sources directory where the assets will be searched
SOURCES_DIR = os.path.join(PROJECT_DIR, '$SOURCES_FROM')
# Templates directory
TEMPLATES_DIR = os.path.join(SOURCES_DIR, 'templates')
# Directory where all stuff will be builded
PUBLISH_DIR = os.path.join(PROJECT_DIR, '_build/dev')
# Path where will be moved all the static files, usually this is a directory in 
# the ``PUBLISH_DIR``
STATIC_DIR = os.path.join(PROJECT_DIR, PUBLISH_DIR, 'static')

# The directory where webassets will store his cache, also you can set this to False to 
# not use the cache, or set it to True to use the default directory from webassets
WEBASSETS_CACHE = os.path.join(PROJECT_DIR, '.webassets-cache')

# The static url to use in templates and with webassets
# This can be a full URL like http://, a relative path or an absolute path
STATIC_URL = 'static/'

# ReSTructuredText parser settings to use when building a RST document
RST_PARSER_SETTINGS = {
    'initial_header_level': 3,
    'file_insertion_enabled': True,
    'raw_enabled': False,
    'footnote_references': 'superscript',
    'doctitle_xform': False,
}

# Extra or custom bundles
EXTRA_BUNDLES = {
    'app_css': Bundle(
        'css/app.css',
        filters='yui_css',
        output='css/app.min.css'
    ),
    'modernizr_js': Bundle(
        "js/foundation/modernizr.foundation.src.js",
        filters='yui_js',
        output='js/modernizr.min.js'
    ),
    'app_js': Bundle(
        "js/foundation/jquery.js",
        "js/foundation/jquery.foundation.forms.js",
        "js/foundation/jquery.foundation.clearing.js",
        "js/foundation/jquery.foundation.magellan.js",
        "js/foundation/jquery.foundation.orbit.js",
        "js/foundation/jquery.foundation.navigation.js",
        "js/foundation/jquery.foundation.accordion.js",
        "js/foundation/jquery.foundation.topbar.js",
        "js/foundation/jquery.cookie.js",
        "js/foundation/jquery.foundation.joyride.js",
        "js/foundation/jquery.foundation.tabs.js",
        "js/foundation/jquery.foundation.buttons.js",
        "js/foundation/jquery.foundation.reveal.js",
        "js/foundation/jquery.event.swipe.js",
        "js/foundation/jquery.foundation.alerts.js",
        "js/foundation/jquery.placeholder.js",
        "js/foundation/jquery.foundation.tooltips.js",
        "js/foundation/jquery.foundation.mediaQueryToggle.js",
        "js/foundation/jquery.event.move.js",
        "js/foundation/app.js",
        filters='yui_js',
        output='js/app.min.js'
    ),
}
# Enabled bundles to use
ENABLED_BUNDLES = ('app_css', 'modernizr_js', 'app_js')

# Sources files or directory to synchronize within the static directory
# This is usually used to put on some assets in the static directory, like images.
# NOTE: You should be carefull to not conflict with files targeted by webassets bundles
FILES_TO_SYNC = (
    #(SOURCE, DESTINATION)
    ('images', 'images'),
)

# Comment, uncomment or add new extension path to use with Jinja here
JINJA_EXTENSIONS = (
    #'compressinja.html.SelectiveHtmlCompressor',
    #'compressinja.html.HtmlCompressor',
)

# This will search for a ``pages`` module that contains page objects
PAGES_MAP = "pages"

# These are the default watcher settings, you can customize them if you want, uncomment 
# parts you want to change, usually you'll change only the "pattern" values
# You don't need to uncomment this if you want to use the watcher with these default 
# parameters

# Templates watcher settings
#WATCHER_TEMPLATES_PATTERNS = {
    #'patterns': ['*.html'],
    #'ignore_patterns': None,
    #'ignore_directories': False,
    #'case_sensitive': False,
#}
# Assets watcher settings
#WATCHER_ASSETS_PATTERNS = {
    #'patterns': ['*.css', '*.js'],
    #'ignore_patterns': None,
    #'ignore_directories': False,
    #'case_sensitive': False,
#}

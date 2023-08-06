"""
This is an Optimus template project for Foundation, the version will follow the version of Foundation
"""
__version__ = "3.2.5"

# Directory structure to create
DIRECTORY_STRUCTURE = [
    # list(dir_name[, children_dir_list])
    [
        'sources',
        [
            ['js'],
            ['css'],
            ['scss'],
            ['images'],
            ['templates'],
        ]
    ]
]

# The directory name that contains 'sources' (assets, templates, images, etc..) in the 
# template project
SOURCES_FROM = 'sources'
# The directory name that will contains 'sources' in the new created projects
SOURCES_TO = SOURCES_FROM

# Default sources files or directory to synchronize within the new project directory
# The sync task is performed before the scripts writing task
FILES_TO_SYNC = (
    #(SOURCE, DESTINATION)
    ('images', 'images'),
    ('js', 'js'),
    ('css', 'css'),
    ('scss', 'scss'),
    ('templates', 'templates'),
)

# Script template files
# NOTE: Files are rendered with the ``String.format()`` method, so remember to double 
#       all your '{' and '}', else they will be interpreted as format variable, and 
#       probably raise a Key error
SCRIPT_FILES = [
    ['requirements.txt', 'requirements.txt'],
    ['gemsets.txt', 'gemsets.txt'],
    ['README.rst', 'README.rst'],
    # Default scripts
    ['scripts/gitignore.tpl', '.gitignore'],
    ['scripts/__init__.py.tpl', '__init__.py'],
    ['scripts/settings.py.tpl', 'settings.py'],
    ['scripts/prod_settings.py.tpl', 'prod_settings.py'],
    ['scripts/pages.py.tpl', 'pages.py'],
    ['scripts/config.rb.tpl', 'config.rb'],
]

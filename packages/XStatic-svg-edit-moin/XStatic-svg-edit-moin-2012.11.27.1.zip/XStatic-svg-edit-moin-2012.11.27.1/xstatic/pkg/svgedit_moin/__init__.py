"""
XStatic resource package

See package 'XStatic' for documentation and basic tools.
"""

DISPLAY_NAME = 'svg-edit-moin' # official name, upper/lowercase allowed
PACKAGE_NAME = 'XStatic-%s' % DISPLAY_NAME # name used for PyPi

NAME = __name__.split('.')[-1] # package name (e.g. 'foo' or 'foo_bar')
                               # please use a all-lowercase valid python
                               # package name

VERSION = '2012.11.27' # for simplicity, use same version x.y.z as bundled files
                       # additionally we append .b for our build number, so we
                       # can release new builds with fixes for xstatic stuff.
BUILD = '1' # our package build number, so we can release new builds
            # with fixes for xstatic stuff.

PACKAGE_VERSION = VERSION + '.' + BUILD # version used for PyPi

DESCRIPTION = "%s %s (XStatic packaging standard)" % (DISPLAY_NAME, VERSION)

PLATFORMS = 'any'
CLASSIFIERS = []
KEYWORDS = '%s xstatic' % NAME

# XStatic-* package maintainer:
MAINTAINER = 'Reimar Bauer'
MAINTAINER_EMAIL = 'rb.proj@googlemail.com'

# this refers to the project homepage of the stuff we packaged:
HOMEPAGE = 'http://code.google.com/p/svg-edit/'

# this refers to all files:
LICENSE = '(same as %s)' % DISPLAY_NAME

from os.path import join, dirname
BASE_DIR = join(dirname(__file__), 'data')
# linux package maintainers just can point to their file locations like this:
#BASE_DIR = '/usr/share/javascript/svg-edit

LOCATIONS = {}


# This package exists to enable
# from degreedays import *
# to import everything that is likely to be needed by an API user in one go.
# It's a bit sloppy, but our classes generally have names that are likely to be
# unique, so it will probably be fine in most cases.  And it's great for example
# code.
# Oddly I couldn't get the example method described at
# http://docs.python.org/2/tutorial/modules.html
# of defining submodules in an __all__ to work.  But importing each package as
# below does work.
from degreedays.api import *
from degreedays.api.data import *
from degreedays.geo import *
from degreedays.time import *

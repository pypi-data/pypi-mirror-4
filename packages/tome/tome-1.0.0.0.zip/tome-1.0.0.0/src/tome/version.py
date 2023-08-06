#!/usr/bin/python
"""
Copyright 2013 Brian Mearns

This file is part of Tome.

Tome is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Tome is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Tome.  If not, see <http://www.gnu.org/licenses/>.
"""

MAJOR = 1
MINOR = 0
PATCH = 0
SEMANTIC = 0

YEAR = 2013
MONTH = 1
DAY = 24
COPYRIGHT = YEAR

#Tag options are None, "dev", and "blood-"*
# None means this is a released/tagged version.
# "dev" means this is a development version from the trunk/mainline.
# "blood" means it's on a branch. After the dash, fill in a short description
# to identify the branch.
#
# Dev and blood versions are still numbered for the *previous* version,
# because we may not know what the next version will be until we're finished.
TAG = None


__months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
assert((MONTH > 0) and (MONTH <= len(__months)))

def setuptools_string():
    vstr = "%d.%d.%d.%d" % (MAJOR, MINOR, PATCH, SEMANTIC)
    if TAG is not None:
        vstr += "-p-%s" % TAG
    return vstr

def string():
    vstr = "%d.%d.%d.%d" % (MAJOR, MINOR, PATCH, SEMANTIC)
    if TAG is not None:
        vstr += "-%s" % TAG
    return vstr

def datestr():
    return "%d %s %02d" % (YEAR, __months[MONTH-1], DAY)


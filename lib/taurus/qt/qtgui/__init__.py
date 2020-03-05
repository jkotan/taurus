#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This package contains a collection of Qt based widgets designed to interact with
taurus models. The widgets are generic in the sence that they do not assume any
behavior associated with a specific HW device. They intend to represent only
abstract model data."""
from __future__ import absolute_import

# register icon path files and icon theme on import of taurus.qt.qtgui
from . import icon as __icon
import os
import sys
import glob
import pkg_resources
from types import ModuleType
from taurus import tauruscustomsettings as __S
from taurus import info as __info
from taurus import warning as __warning


__docformat__ = 'restructuredtext'

icon_dir = os.path.join(os.path.dirname(os.path.abspath(__icon.__file__)))
# TODO: get .path file glob pattern from tauruscustomsettings
__icon.registerPathFiles(glob.glob(os.path.join(icon_dir,'*.path')))
# TODO: get theme name and path from tauruscustomsettings
__icon.registerTheme(name=getattr(__S, 'QT_THEME_NAME', 'Tango'),
                     path=getattr(__S, 'QT_THEME_DIR', ''),
                     force=getattr(__S, 'QT_THEME_FORCE_ON_LINUX', False))

# ------------------------------------------------------------------------
# Note: this is an experimental feature introduced in v 4.3.0a
# It may be removed or changed in future releases

class LazyModule(ModuleType):

    def __init__(self, name, package, entry_point):
        super(LazyModule, self).__init__(name)
        self.__package__ = package
        self.ep = entry_point

    def __getattr__(self, member):
        mod = self.ep.load()
        # Replace lazy module with actual module for package
        setattr(sys.modules[self.__package__], self.__name__, mod)
        # Replace lazy module with actual module in sys.modules
        modname = "%s.%s" % (self.__package__, self.__name__)
        sys.modules[modname] = mod
        return getattr(mod, member)

# Discover the taurus.qt.qtgui plugins
__mod = __modname = None
for __p in pkg_resources.iter_entry_points('taurus.qt.qtgui'):
    try:
        __modname = '%s.%s' % (__name__, __p.name)
        __lazy_mod = LazyModule(__p.name, __name__, __p)
        # Add it to the current module
        setattr(sys.modules[__name__], __p.name, __lazy_mod)
        # Add it to sys.modules
        sys.modules[__modname] = __lazy_mod
        __info('Plugin "%s" loaded as "%s"', __p.module_name, __modname)
    except Exception as e:
        __warning('Could not load plugin "%s". Reason: %s', __p.module_name, e)

# ------------------------------------------------------------------------
    
del (os, glob, __icon, icon_dir, pkg_resources, sys, __mod, __modname, __info,
     __warning)


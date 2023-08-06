# Copyright 2012 Alex Zvoleff
#
# This file is part of the pyabm agent-based modeling toolkit.
# 
# pyabm is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# pyabm is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# pyabm.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact Alex Zvoleff in the Department of Geography at San Diego State 
# University with any comments or questions. See the README.txt file for 
# contact information.

"""
Sets up rc parameters so that they can be loaded and reused by other parts of 
the toolkit.
"""

__version__ = '0.3.3'

import os
import sys
import warnings

import logging

logger = logging.getLogger(__name__)

import numpy as np

from rcsetup import rc_params_management

class IDError(Exception):
    pass

class IDGenerator(object):
    """A generator class for consecutive unique ID numbers. IDs can be assigned 
    externally by other code, and tracked in this class with the use_ID 
    function. The use_ID function will raise an error if called with an ID that has 
    already been assigned."""
    def __init__(self):
        # Start at -1 so the first ID will be 0
        self._last_ID = -1
        self._used_IDs = []

    def reset(self):
        self.__init__()

    def next(self):
        newID = self._last_ID + 1
        while newID in self._used_IDs:
            newID += 1
        self._last_ID = newID
        self._used_IDs.append(newID)
        return newID

    def use_ID(self, used_ID):
        # TODO: This will get very slow when dealing with large numbers of IDs. 
        # It might be better to just set _last_ID to the maximum value in 
        # _used_IDs whenever the use_ID function is called
        if used_ID in self._used_IDs:
            raise IDError("ID %s has already been used"%(used_ID))
        self._used_IDs.append(used_ID)

def boolean_choice(trueProb=.5):
    """A function that returns true or false depending on whether a randomly
    drawn float is less than trueProb"""
    if np.random.rand() < trueProb:
        return True
    else:
        return False

rc_params = rc_params_management()
rc_params.initialize(__name__)

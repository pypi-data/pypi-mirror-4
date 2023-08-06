# Copyright (C) 2011 Versile AS
# 
# This file is part of Versile Python.
# 
# Versile Python is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Other Usage
# Alternatively, this file may be used in accordance with the terms
# and conditions contained in a signed written agreement between you
# and Versile AS.
#
# Versile Python implements Versile Platform which is a copyrighted
# specification that is not part of this software.  Modification of
# the software is subject to Versile Platform licensing, see
# https://versile.com/ for details. Distribution of unmodified
# versions released by Versile AS is not subject to Versile Platform
# licensing.
#

"""Failure objects encapsulating an exception."""


from versile.internal import _vexport

__all__ = ['VFailure']
__all__ = _vexport(__all__)


class VFailure(object):
    """Wrapper object which holds an exception.
    
    Encapsulates exceptions in a non-exception type which allows
    passing as an argument or return value without semantical
    confusion.
    
    """
    def __init__(self, value):
        """Set up on the given exception.

        :param value: an exception
        :type  value: :type:`Exception`
        
        """
        if not isinstance(value, Exception):
            raise TypeError('Value must be an exception')
        self.__value = value

    @property
    def value(self):
        """Exception held by the object."""
        return self.__value

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return repr(self.__value)



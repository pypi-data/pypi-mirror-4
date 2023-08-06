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

"""Exceptions related to :class:`versile.orb.entity.VEntity` operations."""


from versile.internal import _vexport

__all__ = ['VEntityError', 'VEntityReaderError', 'VEntityWriterError',
           'VLinkError']
__all__ = _vexport(__all__)


class VEntityError(Exception):
    """General :class:`versile.orb.entity.VEntity` related error."""

    
class VEntityReaderError(Exception):
    """General :class:`versile.orb.entity.VEntity` reader error."""


class VEntityWriterError(Exception):
    """General :class:`versile.orb.entity.VEntity` writer error."""


class VLinkError(Exception):
    """General :class:`versile.orb.link.VLink` handling error."""

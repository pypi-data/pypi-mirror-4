# Copyright (C) 2011-2013 Versile AS
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


"""Global configuration."""


from threading import Lock

from versile.internal import _vexport, _pyver

__all__ = ['Versile']
__all__ = _vexport(__all__)


class Versile(object):
    """Global Versile Python configuration.

    Before a :class:`versile.orb.link.VLink` or
    :class:`versile.orb.service.VService` is constructed, the license
    type of Versile Python must be specified on :class:`Versile` as a
    global configuration. This requires calling one of the class
    methods :meth:`set_agpl`\ , :meth:`set_agpl_internal_use` or
    :meth:`set_commercial`\ . This is because this information is
    required for the :term:`VOL` protocol for performing a link
    handshake.
    
    """
    
    # Lock for access to _copyleft* attributes
    _copyleft_lock = Lock()

    # True if Versile Python is running with a license or otherwise
    # linked with software which grants copyleft license type rights
    # to networked peers, as defined by the Versile ORB Link protocol.
    # Default value is None; it must be explicitly set to True or False
    # before a link can be negotiated with a peer.
    _copyleft = None

    # A string to a copyleft license name if _copyleft is True,
    # e.g. 'AGPLv3'
    _copyleft_license = None

    # If _copyleft is True, a string with a URL to a resource which
    # provides license information and instructions how to obtain software
    _copyleft_url = None

    @classmethod
    def set_agpl(cls, url, other_lic=None):
        """Configures Versile Python to be running with an AGPLv3 license.

        :param url:       valid URL for license text and download instructions
        :type  url:       unicode
        :param other_lic: if not None, license type for other licenses
        :type  other_lic: unicode
        :raises:          :exc:`exceptions.TypeError`

        *url* must begin with either 'http://', 'https://', or 'vop://'
        as per :term:`VOL` protocol specifications.

        If Versile Python is linked with other products which grants
        additional copyleft type rights, then *other_lic* should be a
        string which contains the appropriate license names. A license
        type for the link will then be composed as the string 'AGPLv3, '
        concatenated with *other_lic*\ .

        Raises an exception if url or other_lic (if provided) is not
        of unicode type (python v2) or str (python v3).

        .. note::

            Setting up Versile Python to be running with an AGPLv3 license
            will cause created :term:`VOL` links to provide this license
            information during link handshake, as per the :term:`VOL`
            protocol specifications.
        
        """
        if _pyver == 2:
            _typ = str
            if isinstance(url, str):
                url = _typ(url)
            if other_lic and isinstance(other_lic, str):
                other_lic = str(other_lic)
        else:
            _typ = str
        if not isinstance(url, _typ):
            raise TypeError('URL must be string')
        if other_lic and not isinstance(other_lic, _typ):
            raise TypeError('Other license must be string')
        lic = 'AGPLv3, '
        if other_lic:
            lic += other_lic

        _lurl = url.lower()
        if not (_lurl.startswith('http://') or
                _lurl.startswith('https://') or
                _lurl.startswith('vop://')):
            raise TypeError('URL must start with \'http://\', \'https://\'' +
                            'or \'vop://\'')

        Versile._copyleft_lock.acquire()
        try:
            Versile._copyleft = True
            Versile._copyleft_license = lic
            Versile._copyleft_url = url
        finally:
            Versile._copyleft_lock.release()
        
    @classmethod
    def set_agpl_internal_use(cls):
        """Configures Versile Python with AGPLv3 license for internal use only.
        
        Copyleft of AGPLv3 applies when distributing code or providing
        networked access to a person or organization which is outside
        of the legal entity which is licensing the software in
        question, so it is normally possible for an organization to
        run AGPLv3 licensed software without distributing source, as
        long as the software is used and distributed strictly within
        that organization. In this case, download instructions may not
        apply, and for such use cases calling :meth:`set_agpl` to
        point to such a URL may not be appropriate.

        If this method is called, Versile Python is configured for
        being used with an AGPLv3 license, to be used and distributed
        strictly within one single organization. It works similarly to
        :meth:`set_agpl`\ , however for convenience it will set *url*
        to point to a page on the Versile web site which clarifies the
        license and its limitations.
        
        .. note::

            Setting up Versile Python to be running with an AGPLv3
            license for internal only use will cause created
            :term:`VOL` links to provide this license information
            during link handshake, as per the :term:`VOL` protocol
            specifications.
        
        """
        Versile._copyleft_lock.acquire()
        try:
            Versile._copyleft = True
            Versile._copyleft_license = 'AGPLv3'
            _url = 'https://versile.com/resource/agplv3_internal_use_only/'
            Versile._copyleft_url = _url
        finally:
            Versile._copyleft_lock.release()
        
    @classmethod
    def set_commercial(cls):
        """Configures Versile Python to be running with commercial license.

        .. note::

            Setting up Versile Python to be running with a commercial license
            will cause created :term:`VOL` links to provide this license
            information during link handshake, as per the :term:`VOL`
            protocol specifications.
        
        """
        Versile._copyleft_lock.acquire()
        try:
            Versile._copyleft = False
            Versile._copyleft_license = None
            Versile._copyleft_url = None
        finally:
            Versile._copyleft_lock.release()
    
    @classmethod
    def copyleft(cls):
        """Returns configured Versile Python copyleft license information.

        :returns: tuple of license information
        :rtype:   (bool, unicode, unicode)
        
        Returns 3-tuple of the following elements:

        * True if set to run with copyleft license, otherwise False
        * If copyleft license, the configured license name(s)
        * If copyleft license, URL to license and download instructions
        
        """
        Versile._copyleft_lock.acquire()
        try:
            return (Versile._copyleft, Versile._copyleft_license,
                    Versile._copyleft_url)
        finally:
            Versile._copyleft_lock.release()

    @classmethod
    def _reset_copyleft(cls):
        """Resets globally configured copyleft information.
        
        Intended for internal usage by the platform.
        
        """
        Versile._copyleft_lock.acquire()
        try:
            Versile._copyleft = None
            Versile._copyleft_license = None
            Versile._copyleft_url = None 
        finally:
            Versile._copyleft_lock.release()

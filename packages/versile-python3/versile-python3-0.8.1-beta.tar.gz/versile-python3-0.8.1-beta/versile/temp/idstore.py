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

"""Identity store.

    .. warning::

        This module is a temporary structure which is not part of the
        :term:`VPy` framework and will be replaced in later versions.
    
"""


import os
import sqlite3

from versile.internal import _vexport, _val2b
from versile.common.util import VLockable

__all__ = ['XIdentityStore']
__all__ = _vexport(__all__)


class XIdentityStore(VLockable):
    """A simple identity store for identity keys and associated identity names.
    
    :param filename: filename of identity manager database
    :param filename: str

    .. warning::

        This class is a temporary structure which is not part of the
        :term:`VPy` framework and will be replaced in later versions.
    
    """
    
    def __init__(self, filename):
        super(XIdentityStore, self).__init__()
        if not os.path.exists(filename):
            raise IOError('No such file')
        self._conn = sqlite3.connect(filename, check_same_thread=False)

    def link_authorizer(self, permission):
        """Returns a link authorizer.

        :param permission: permission name to check against
        :type  permission: unicode
        :returns:          link authorizer function.
        :rtype:            callable
        
        Returns a link authorization function in the format taken by a
        :class:`versile.orb.VLink` by its constructor *auth*
        argument.

        The generated authorized only checks the identity key of the
        link's context object and does not check certificates or
        claimed identity. It also ignores peer host information.
        
        """ 
        return lambda link: self._authorize_link(link, permission)

    def authorizer(self, permission):
        """Returns an authorizer object.
        
        :param permission: permission name to check against
        :type  permission: unicode
        :returns:          authorizer object
        :rtype:            :class:`versile.crypto.auth.VAuth`
        
        Returns an authorizer which checks an identity key has the
        defined *permission*.
        
        The authorizer ignores certificate information or claimed
        identity information. The authorizer allows any peer host and
        only verifies identity key against key store data.
        
        """ 
        store = self
        from versile.crypto.auth import VAuth
        class _Auth(VAuth):
            def accept_credentials(self, key, identity, certificates):
                try:
                    return store.identity_has_permission(key, permission)
                except:
                    return False
        return _Auth()
        
    def add_identity(self, key, allowed=True):
        """Adds an identity.
        
        :param key:      identity key to add to manager database
        :type  key:      :class:`versile.crypto.VAsymmetricKey`
        :param allowed:  if True this key is an allowed key
        :type  allowed:  bool
        :raises:         :exc:`exceptions.ValueError`
        
        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()        
            c.execute('insert into identity values(null, ?, ?)',
                      (sqlite3.Binary(_keydata), int(allowed)))
            self._conn.commit()

    def remove_identity(self, key):
        """Removes an identity.
        
        :param key:      identity key
        :type  key:      :class:`versile.crypto.VAsymmetricKey`
        
        """
        with self:
            c = self._conn.cursor()
            _keydata = self._keyblob(key)
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute('delete from id_perm where identity_id = ?', (i_id,))
            c.execute('delete from id_group where identity_id = ?', (i_id,))
            c.execute('delete from identity where _id = ?', (i_id,))
            self._conn.commit()

    def add_group(self, name):
        """Adds a group.
        
        :param name: group name
        :type  name: unicode
        
        """
        with self:
            c = self._conn.cursor()        
            c.execute('insert into _group values(null, ?)', (name,))
            self._conn.commit()

    def remove_group(self, name):
        """Removes a group.
        
        :param name: group name
        :type  name: unicode
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (name,))
            g_id = list(c)[0][0]
            c.execute('delete from group_perm where group_id = ?', (g_id,))
            c.execute('delete from _group where _id = ?', (g_id,))
            self._conn.commit()
            
    def add_permission(self, name):
        """Adds a permission.
        
        :param name: permission name
        :type  name: unicode
        
        """
        with self:
            c = self._conn.cursor()        
            c.execute('insert into permission values(null, ?)', (name,))
            self._conn.commit()

    def remove_permission(self, name):
        """Removes a permission.
        
        :param name: permission name
        :type  name: unicode
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from permission where name = ?',
                      (name,))
            p_id = list(c)[0][0]
            c.execute('delete from id_perm where permission_id = ?', (p_id,))
            c.execute('delete from group_perm where permission_id = ?',
                      (p_id,))
            c.execute('delete from permission where _id = ?', (p_id,))
            self._conn.commit()

    def group_add_identity(self, group, key):
        """Associates identity with group.
        
        :param group: name of group to associate with
        :type  group: unicode
        :param key:   identity's key
        :type  key:   :class:`versile.crypto.VAsymmetricKey`
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (group,))
            g_id = list(c)[0][0]
            _keydata = self._keyblob(key)
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute('''
            select * from id_group where identity_id = ? and group_id = ?
            ''', (i_id, g_id))
            if not list(c): 
                c.execute('insert into id_group values(?, ?)', (i_id, g_id))
                self._conn.commit()

    def group_remove_identity(self, group, key):
        """Removes identity from group.
        
        :param group: name of group
        :type  group: unicode
        :param key:   identity's key
        :type  key:   :class:`versile.crypto.VAsymmetricKey`
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (group,))
            g_id = list(c)[0][0]
            _keydata = self._keyblob(key)
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute('''
            delete from id_group where identity_id = ? and group_id = ?
            ''', (i_id, g_id))
            self._conn.commit()

    def identity_add_permission(self, key, permission):
        """Sets permission for an identity.
        
        :param key:        identity's key
        :type  key:        :class:`versile.crypto.VAsymmetricKey`
        :param permission: name of permission
        :type  permission: unicode
        
        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute('select _id from permission where name = ?',
                      (permission,))
            p_id = list(c)[0][0]
            c.execute('''
            select * from id_perm
                where identity_id = ? and permission_id = ?
            ''', (i_id, p_id))
            if not list(c): 
                c.execute('insert into id_perm values(?, ?)',
                          (i_id, p_id))
                self._conn.commit()
        
    def identity_remove_permission(self, key, permission):
        """Removes permission for an identity.
        
        :param key:        identity's key
        :type  key:        :class:`versile.crypto.VAsymmetricKey`
        :param permission: name of permission
        :type  permission: unicode
        
        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute('select _id from permission where name = ?',
                      (permission,))
            p_id = list(c)[0][0]
            c.execute('''
            delete from id_perm
                where identity_id = ? and permission_id = ?
            ''', (i_id, p_id))
            self._conn.commit()
        
    def group_add_permission(self, group, permission):
        """Sets permission for a group.
        
        :param group:      name of group
        :type  group:      unicode
        :param permiss     ion: name of permission
        :type  permission: unicode
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (group,))
            g_id = list(c)[0][0]
            c.execute('select _id from permission where name = ?',
                      (permission,))
            p_id = list(c)[0][0]
            c.execute('''
            select * from group_perm
                where group_id = ? and permission_id = ?
            ''', (g_id, p_id))
            if not list(c): 
                c.execute('insert into group_perm values(?, ?)',
                          (g_id, p_id))
                self._conn.commit()
    
    def group_remove_permission(self, group, permission):
        """Removes permission for a group.
        
        :param group:      name of group
        :type  group:      unicode
        :param permiss     ion: name of permission
        :type  permission: unicode
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (group,))
            g_id = list(c)[0][0]
            c.execute('select _id from permission where name = ?',
                      (permission,))
            p_id = list(c)[0][0]
            c.execute('''
            delete * from group_perm
                where group_id = ? and permission_id = ?
            ''', (g_id, p_id))
            self._conn.commit()
    
    def identity_set_allowed(self, key, allowed):
        """Sets the *allowed* state of an identity
        
        :param key:      identity's key
        :type  key:      :class:`versile.crypto.VAsymmetricKey`
        :param allowed:  if True this key is an allowed key
        :type  allowed:  bool

        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()
            c.execute('update services set allowed = ? where data like ?',
                      (int(allowed), _keydata,))
            self._conn.commit()

    def identity_permissions(self, key):
        """Returns permissions registered on identity.

        :param key:  identity's key
        :type  key:  :class:`versile.crypto.VAsymmetricKey`
        :returns:    (permission name,)
        
        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute(
            '''select permission.name from id_perm
                   inner join permission
                       on id_perm.permission_id = permission._id
                   where id_perm.identity_id = ?
            ''', (i_id,))
            return tuple(item[0] for item in c)

    def identity_groups(self, key):
        """Returns groups registered on identity.

        :param key:  identity's key
        :type  key:  :class:`versile.crypto.VAsymmetricKey`
        :returns:    (group name,)
        
        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()
            c.execute('select _id from identity where data like ?',
                      (_keydata,))
            i_id = list(c)[0][0]
            c.execute('''select _group.name from _group
                inner join id_group
                    on _group._id = id_group.group_id
                where id_group.identity_id = ?
            ''', (i_id,))
            return tuple(item[0] for item in c)            

    def identity_has_permission(self, key, permission, check_groups=True):
        """Returns True if identity has given permission.
        
        :param key:          identity's key
        :type  key:          :class:`versile.crypto.VAsymmetricKey`
        :param permission:   permission name to check
        :type  permission:   unicode
        :param check_groups: if True also check permissions via groups
        :type  check_groups: bool
        :returns:            True if identity is allowed and has permission
        
        """
        with self:
            _keydata = self._keyblob(key)
            c = self._conn.cursor()
            c.execute('select _id, allowed from identity where data like ?',
                      (_keydata,))
            i_id, allowed = list(c)[0]
            if not allowed:
                return False
            c.execute('select _id from permission where name = ?',
                      (permission,))
            p_id = list(c)[0][0]
            c.execute('''
            select * from id_perm
                where identity_id = ? and permission_id = ?
            ''', (i_id, p_id))
            if list(c):
                return True            
            if check_groups:
                for group in self.identity_groups(key):
                    if permission in self.group_permissions(group):
                        return True
            return False
        
    def group_identities(self, group):
        """Returns identities registered on group.

        :param group: group name
        :type  group: unicode
        :returns:     (identity key,)
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (group,))
            g_id = list(c)[0][0]
            c.execute('''select identity.data from identity
                inner join id_group
                    on identity._id = id_group.identity_id
                where id_group.group_id = ?
            ''', (g_id,))
            from versile.crypto import VCrypto
            _factory = VCrypto().lazy().num_rsa.key_factory
            result = []
            for item in c:
                _keydata = b''.join(item[0])
                _keydata = _keydata.split(':')[1]
                n, e = _keydata.split(',')
                _keydata = (int(n), int(e), None, None, None)
                result.append(_factory.load(_keydata))
            return tuple(result)
            
    def group_permissions(self, group):
        """Returns permissions registered on group.
        
        :param group: group name
        :type  group: unicode
        :returns:     (permission name,)
        
        """
        with self:
            c = self._conn.cursor()
            c.execute('select _id from _group where name = ?', (group,))
            g_id = list(c)[0][0]
            c.execute(
            '''select permission.name from group_perm
                   inner join permission
                       on group_perm.permission_id = permission._id
                   where group_perm.group_id = ?
            ''', (g_id,))
            return tuple(item[0] for item in c)

    @property
    def identities(self):
        """Holds keydata of registered identities."""
        c = self._conn.cursor()
        c.execute('select data from identity')
        from versile.crypto import VCrypto
        _factory = VCrypto().lazy().num_rsa.key_factory
        result = []
        for item in c:
            _keydata = b''.join(item[0])
            _keydata = _keydata.split(':')[1]
            n, e = _keydata.split(',')
            _keydata = (int(n), int(e), None, None, None)
            result.append(_factory.load(_keydata))
        return tuple(result)

    @property
    def groups(self):
        """Holds a tuple of group names."""
        c = self._conn.cursor()
        c.execute('select name from _group')
        return tuple(item[0] for item in c)
    
    @property
    def permissions(self):
        """Holds a tuple of permission names."""
        c = self._conn.cursor()
        c.execute('select name from permission')
        return tuple(item[0] for item in c)        
    
    @classmethod
    def create(cls, filename):
        """Creates a new identity management database file.
        
        :param filename:  filename of database
        :returns:         manager for the new database
        :rtype:           :class:`XIdentityStore`
        :raises:          :exc:`exceptions.IOError`
        
        """
        if os.path.exists(filename):
            raise IOError('File already exists')
        conn = sqlite3.connect(filename, check_same_thread=False)
        
        c = conn.cursor()
        c.execute('''
        create table identity (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            data BLOB UNIQUE,
            allowed INTEGER
        )''')
        c.execute('''
        create table permission (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )''')
        c.execute('''
        create table _group (
            _id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )''')
        c.execute('''
        create table id_group (
            identity_id INTEGER,
            group_id INTEGER
        )''')
        c.execute('''
        create table id_perm (
            identity_id INTEGER,
            permission_id INTEGER
        )''')
        c.execute('''
        create table group_perm (
            group_id INTEGER,
            permission_id INTEGER
        )''')
        conn.commit()
        
        return cls(filename)

    def _authorize_link(self, link, permission):
        with self:
            ctx = link.context
            key, chain = ctx.credentials
            try:
                valid = self.identity_has_permission(key, permission)
            except:
                return False
            else:
                if valid:
                    ctx._v_authorize()
                return valid
            
    @classmethod
    def _keyblob(cls, key):
        if not key.cipher_name == 'rsa':
            raise ValueError('Invalid key type, must be RSA key')
        n, e = key.keydata[:2]
        if n is None or e is None:
            raise ValueError('Public RSA key components missing')
        return b''.join((b'rsa:', _val2b(n), b',', _val2b(e)))
        

#!/usr/bin/env python
#
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

from distutils.core import setup
import os


# Release number
release = '0.8.1-beta'
py_version = 3

# General settings
provides = 'versile_python3'
author = 'Versile AS'
author_email = 'versile_python@versile.com'
url = 'http://versile.com/'

# AGPL related settings
name = 'versile-python3'
long_name = 'Versile Python'
lic = 'Choice of (a) GNU Affero GPL v3 License, or (b) Commercial License'
lic_cl_open = 'License :: OSI Approved :: GNU Affero General Public License v3'
lic_cl_com = 'License :: Other/Proprietary License'

ldesc = """

Versile Python
--------------

Versile Python is an implementation of Versile Platform for python
v3.x. See the `product website
<https://versile.com/products/vpy/>`__ for documentation and
additional product information.

Versile Platform
----------------

Versile Platform is a set of open protocols enabling object-level
service interaction between heterogenous technologies. The protocols
are designed to enable simple yet flexible and powerful patterns for
interacting with remote services or running services. See the
`platform website <https://versile.com/platform/>`__ for more
information.

"""
ldesc = ldesc.strip() + '\n'

# Package meta-data
cf = ['Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      lic_cl_open,
      lic_cl_com,
      'Natural Language :: English',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Operating System :: Unix',
      'Topic :: Communications',
      'Topic :: Internet',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Software Development :: Object Brokering'
      ]
if py_version == 2:
    cf.extend(['Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7'
               ])
elif py_version == 3:
    cf.append('Programming Language :: Python :: 3')
    

# Packages under ./versile/
packages = []
for dirpath, dirs, files in os.walk('versile'):
    if '__init__.py' in files:
        packages.append(dirpath.replace(os.path.sep, '.'))


if __name__ == '__main__':
    setup(name=name,
          version=release,
          description=long_name,
          long_description=ldesc,
          provides=[provides],
          author=author,
          author_email=author_email,
          maintainer=author,
          maintainer_email=author_email,
          url=url,
          packages=packages,
          keywords=['versile'],
          classifiers=cf,
          license=lic
          )

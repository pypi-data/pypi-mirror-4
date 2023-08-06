Versile Python -- implementation of Versile Platform.

Copyright (C) 2011-2013 Versile AS


Overview
--------

Versile Python is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program.  If not, see
<http://www.gnu.org/licenses/>.

Other Usage
Alternatively, Versile Python may be used in accordance with the
terms and conditions contained in a signed written agreement between
you and Versile AS.

Versile Python implements Versile Platform which is a copyrighted
specification that is not part of this software.  Modification of
the software is subject to Versile Platform licensing, see
https://versile.com/ for details. Distribution of unmodified
versions released by Versile AS is not subject to Versile Platform
licensing.


Availability
------------

This is the source distribution of Versile Python for python
v3.x. The latest version of this software can be downloaded
from https://versile.com/

Versile Python comes in two distributions, one distribution for python
2.6 and 2.7 and a second distribution for python 3.x. The two
distributions share a common codebase and the 3.x distribution is
generated from the 2.x codebase with the python '2to3' migration tool.


Installation
------------

This package comes with a distutils installation script. To install
execute the following command in a shell:

    "python setup.py install"

Note the command may have to be executed with administrative
privileges (e.g. sudo or a root shell) and depending on setup a full
path to the executable may need to be provided. Also ensure the python
executable is compatible with python versions v3.x.

It is strongly recommended to also download and install PyCrypto
(https://www.dlitz.net/software/pycrypto/) if available on the
platform. When present it will significantly speed up cryptographic
methods and enable additional ciphers such as AES.

For testing or user-specific installations consider using virtualenv,
see http://pypi.python.org/pypi/virtualenv


Bugs and Patches
----------------

See https://versile.com/ for information how to report bugs and how to obtain 
the latest version.


Documentation
-------------

Browse or download documentation at https://versile.com/


Additional Information
----------------------

This is a beta release. APIs may change in later releases.

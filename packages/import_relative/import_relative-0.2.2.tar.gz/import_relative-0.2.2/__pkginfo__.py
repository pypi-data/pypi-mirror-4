# Copyright (C) 2008-2009, 2013 Rocky Bernstein <rocky@gnu.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""packaging information"""

modname = 'import_relative'

import os
me = os.path.join(os.path.dirname(__file__), 'VERSION.py')
exec(compile(open(me).read(), me, 'exec'))

version      = VERSION
web          = 'http://code.google.com/p/pyimport-relative'

short_desc = 'A different kind of relative import'

author = "Rocky Bernstein"
author_email = "rocky@gnu.org"

classifiers =  ['Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]
# download_url = '%s-%s.egg' % (modname, version,)

py_modules = [modname]

web = 'http://code.google.com/p/pyimport-relative'

zip_safe = False # tracebacks in zip files are funky and not debuggable

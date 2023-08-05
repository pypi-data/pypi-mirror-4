#
#   Copyright 2011 Olivier Kozak
#
#   This file is part of Mocki.
#
#   Mocki is free software: you can redistribute it and/or modify it under the
#   terms of the GNU Lesser General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   Mocki is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#   details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with Mocki. If not, see <http://www.gnu.org/licenses/>.
#

import distutils.core

distutils.core.setup(
    name='Mocki',
    version='1.5',
    description='An easy-to-use but full featured mocking library for Python.',
    url='https://launchpad.net/mocki',
    author='Olivier Kozak',
    author_email='olivier.kozak@gmail.com',
    license='GNU LGPL v3',
    packages=('mocki',)
)

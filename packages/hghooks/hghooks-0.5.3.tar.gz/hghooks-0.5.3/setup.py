# Copyright (c) 2010 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup

from hghooks import version


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name="hghooks",
    version=version,
    author="Lorenzo Gil Sanchez",
    author_email="lorenzo.gil.sanchez@gmail.com",
    description="A set of useful hooks for Mercurial",
    long_description='\n\n'.join([read('README.txt'), read('CHANGES.txt')]),
    license="LGPL 3",
    keywords="mercurial pep8 pyflakes trac",
    packages=['hghooks'],
    url='http://bitbucket.org/lgs/hghooks/',
    zip_safe=False,
    install_requires=['setuptools'],
    entry_points={
        'hghooks.trac.ticket_commands': [
            'default = hghooks.trachooks:default_ticket_commands',
            ],
        'hghooks.trac.token_commands': [
            'default = hghooks.trachooks:default_token_commands',
            ],
       },
)

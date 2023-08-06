# -*- coding: utf-8 -*-
# Copyright (c) 2013 by Pablo Martín <goinnn@gmail.com>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='Kate-plugins',
    version="0.2.1",
    description="Plugins to Kate editor to develop faster python projects, django projects and something of javascript",
    long_description=(read('README.rst') + '\n\n' + read('CHANGES.rst')),
    author="Pablo Martin",
    author_email="goinnn@gmail.com",
    url="https://github.com/goinnn/Kate-plugins",
    license="GNU Lesser General Public License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development",
    ],
    install_requires=[
        "pysmell==0.7.3",
        "pep8==0.6.1",
        "pyflakes==0.5.0",
        "pyjslint==0.3.3",
        "pyplete==0.0.2",
        "simplejson==2.6.1"
    ],
    packages=('kate_plugins', ),
    keywords="kate,pate,plugins,kate plugins,pate plugins,python,autocomplete,autocomplete python,django,jquery,js,checker,pep8,pyflakes,jslint",
    include_package_data=True,
    zip_safe=False,
)

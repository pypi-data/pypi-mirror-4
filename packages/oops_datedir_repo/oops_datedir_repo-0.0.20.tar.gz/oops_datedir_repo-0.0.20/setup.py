#!/usr/bin/env python
#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).
  

from distutils.core import setup
import os.path

description = file(os.path.join(os.path.dirname(__file__), 'README'), 'rb').read()

setup(name="oops_datedir_repo",
      version="0.0.20",
      description="OOPS disk serialisation and repository management.",
      long_description=description,
      maintainer="Launchpad Developers",
      maintainer_email="launchpad-dev@lists.launchpad.net",
      url="https://launchpad.net/python-oops-datedir-repo",
      packages=['oops_datedir_repo'],
      package_dir = {'':'.'},
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      install_requires = [
          'bson',
          'iso8601',
          'launchpadlib', # Needed for pruning - perhaps should be optional.
          'oops',
          'pytz',
          ],
      extras_require = dict(
          test=[
              'fixtures',
              'testtools',
              ]
          ),
        entry_points=dict(
            console_scripts=[ # `console_scripts` is a magic name to setuptools
                'bsondump = oops_datedir_repo.bsondump:main',
                'prune = oops_datedir_repo.prune:main',
                ]),
      )

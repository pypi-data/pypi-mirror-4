#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

from distutils.core import setup

setup(name='pyspread',
      version='0.2.3',
      description='Python spreadsheet',
      long_description='Pyspread is a non-traditional spreadsheet application'
                       ' that is based on and written in the programming '
                       'language Python.',
      license='GPL v3 :: GNU General Public License',
      keywords=['spreadsheet', 'pyspread'],
      author='Martin Manns',
      author_email='mmanns@gmx.net',
      url='http://manns.github.com/pyspread/',
      requires=['numpy (>=1.1)', 'wx (>=2.8.10)', 'matplotlib (>=1.1.1)',
                'python_gnupg (>=0.3.0)'],
      packages=['pyspread'],
      scripts=['pyspread/pyspread'],
      package_data={'pyspread':
        ['*.py',
         '../pyspread.sh',
         'src/*.py',
         'src/pyspread',
         'src/*/*.py',
         'src/*/test/*.py',
         'src/*/test/*.pys*',
         'src/*/test/*.sig',
         'src/*/test/*.csv',
         'src/*/test/*.txt',
         'src/*/test/*.pys*',
         'share/icons/*.png',
         'share/icons/Tango/24x24/actions/*.png',
         'share/icons/Tango/24x24/toggles/*.png',
         'share/icons/Tango/24x24/toggles/*.xpm',
         'doc/help/*.html',
         'doc/help/images/*.png',
         'locale/*/*/*.mo',
         'examples/*',
         'COPYING', 'thanks', 'faq',
         'authors', '../pyspread.pth', '../README', '../changelog']},
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
      ],
)
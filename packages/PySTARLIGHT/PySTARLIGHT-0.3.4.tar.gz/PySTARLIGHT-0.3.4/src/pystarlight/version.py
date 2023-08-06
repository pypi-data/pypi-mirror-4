'''
Created on Feb 15, 2013

@author: william
'''
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# metadata definition used by setup.py and others

_pystarlight_version_          = "0.3.4"
_pystarlight_name_             = "PySTARLIGHT"
_pystarlight_copyright_        = '2012, A. L. De Amorim, W. Schoenell, N. V. Asari'
_pystarlight_requires_         = ['numpy', 'scipy', 'atpy', 'matplotlib', 'pyfits', 'asciitable']
_pystarlight_provides_         = ['pystarlight']
_pystarlight_packages_         = ['pystarlight', 'pystarlight.io', 'pystarlight.plots', 'pystarlight.util']

_pystarlight_updated_          = '2013-02-15'

_pystarlight_description_      = 'Python utilities for STARLIGHT'
_pystarlight_long_description_ = 'Python utilities for STARLIGHT'
_pystarlight_author_           = 'Andre Luiz de Amorim, William Schoenell, Natalia Vale Asari'
_pystarlight_author_email_     = 'andre@astro.ufsc.br, william@iaa.es, natalia@astro.ufsc.br'
_pystarlight_license_          = "GPLv2"
_pystarlight_url_              = 'http://www.starlight.ufsc.br/'
_pystarlight_download_url_     = 'https://bitbucket.org/astro_ufsc/pystarlight/get/%s-%s.tar.bz2' % (_pystarlight_name_, _pystarlight_version_)
_pystarlight_platform_         = "GNU/Linux"
_pystarlight_classifiers_      = [ 'Development Status :: 4 - Beta',
                                   'Environment :: Console',
                                   'Intended Audience :: Science/Research',
                                   'Intended Audience :: Developers',
                                   'License :: OSI Approved :: GNU General Public License (GPL)',
                                   'Natural Language :: English',
                                   'Natural Language :: Portuguese (Brazilian)',                               
                                   'Operating System :: POSIX :: Linux',
                                   'Programming Language :: Python',
                                   'Topic :: Scientific/Engineering :: Astronomy']

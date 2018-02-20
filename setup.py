#!/usr/bin/env python
# This file is based havily on the astropy version here:
# https://github.com/astropy/package-template/blob/master/setup.py
# Which is licensed under the astropy license.

import glob
import os
import sys

import ah_bootstrap
from setuptools import setup

# A dirty hack to get around some early import/configurations ambiguities
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins._ASTROPY_SETUP_ = True

# -- Read the Docs Setup  -----------------------------------------------------

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if on_rtd:
    os.environ['HOME'] = '/home/docs/'
    os.environ['SUNPY_CONFIGDIR'] = '/home/docs/'

from astropy_helpers.setup_helpers import (
    register_commands, get_debug_option, get_package_info)
from astropy_helpers.git_helpers import get_git_devstr
from astropy_helpers.version_helpers import generate_version_py

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'packagename')
DESCRIPTION = metadata.get('description', 'SunPy: Python for Solar Physics')
AUTHOR = metadata.get('author', 'The SunPy Community')
AUTHOR_EMAIL = metadata.get('author_email', 'sunpy@googlegroups.com')
LICENSE = metadata.get('license', 'BSD 2-Clause')
URL = metadata.get('url', 'http://sunpy.org')

LONG_DESCRIPTION = "SunPy is a Python library for solar physics data analysis."

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = '0.8.4'

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behavior.
cmdclassd = register_commands(PACKAGENAME, VERSION, RELEASE)

try:
    from sunpy.tests.setup_command import SunPyTest
    # Overwrite the Astropy Testing framework
    cmdclassd['test'] = type('SunPyTest', (SunPyTest,),
                            {'package_name': 'sunpy'})

except Exception:
    # Catch everything, if it doesn't work, we still want SunPy to install.
    pass

# Freeze build information in version.py
generate_version_py(PACKAGENAME, VERSION, RELEASE,
                    get_debug_option(PACKAGENAME))

# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']


# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
package_info = get_package_info()

# Add the project-global data
package_info['package_data'].setdefault(PACKAGENAME, [])

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith('.c'):
            c_files.append(
                os.path.join(
                    os.path.relpath(root, PACKAGENAME), filename))
package_info['package_data'][PACKAGENAME].extend(c_files)

extras_require = {'database': ["sqlalchemy"],
                  'image': ["scikit-image"],
                  'jpeg2000': ["glymur"],
                  'net': ["suds-jurko", "beautifulsoup4", "requests", "dateutil"],
                  'tests': ["pytest", "pytest-cov", "pytest-mock", "pytest-rerunfailures", "mock", "hypothesis"]}
extras_require['all'] = extras_require['database'] + extras_require['image'] + \
                        extras_require['net'] + extras_require['tests']

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      scripts=scripts,
      install_requires=['numpy>=1.11',
                        'astropy>=2.0',
                        'scipy',
                        'pandas>=0.12.0',
                        'matplotlib>=1.3'],
      extras_require=extras_require,
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      long_description=LONG_DESCRIPTION,
      cmdclass=cmdclassd,
      zip_safe=False,
      use_2to3=False,
      include_package_data=True,
      **package_info
      )

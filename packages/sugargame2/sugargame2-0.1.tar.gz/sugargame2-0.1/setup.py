#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Find the version from the package metadata.

import os
import re

package_version = re.search(
    "__version__ = '([^']+)'",
    open(os.path.join('sugargame2', '__init__.py')).read()).group(1)

# Dependencies
# - While Pygame is listed as a dependency, you should install it separately to
#   avoid issues with libpng and others.
#   See: http://www.pygame.org/install.html

setup(
    name='sugargame2',
    version=package_version,
    author='Platipy Project',
    author_email='platipy@platipy.org',
    install_requires=['setuptools', 'pygame>=1.8'],
    packages=['sugargame2'],
    description='A fork of sugargame, a module for using pygame in the Sugar toolkit',
    long_description=open('README.rst', 'r').read(),
    keywords="pygame game engine sugar olpc",
    license='BSD',
    url='https://github.com/platipy/sugargame2',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: pygame',
    ]
)

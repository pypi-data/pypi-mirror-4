#!python
# StuphOS Setup
# --
# Copyright 2013 Clint Banis.  All rights reserved.
#
'%(main_documentation)s' # (RST-Enabled)
import os; del os.link # HA!

__author__ = 'Clint Banis'
__author_email__ = 'cbanis@gmail.com'
__url__ = "http://stuphmud.net:2184"

# PyPI Metadata (PEP 301)
SETUP_CONF = \
dict (name = "stuphos-lite",
      description = "StuphOS embedded runtime configuration (lite release).",

      download_url = __url__,

      license = "BSD",
      platforms = ['POSIX', 'Linux', 'Cygwin', 'OS-independent', 'Many'],

      include_package_data = True,

      keywords = ['stuphos', 'stuphmud', 'stuph', 'mud', 'circlemud', 'circle'],

      classifiers = ['Development Status :: 2 - Pre-Alpha',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2',
                     # 'Programming Language :: Python :: 3',
                     'Operating System :: OS Independent',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Topic :: Software Development :: Embedded Systems',
                     'Topic :: Software Development :: Libraries :: Application Frameworks',
                     'Topic :: System :: Networking',
                     'Topic :: System :: Distributed Computing',
                     'Topic :: System :: Systems Administration',
                     'Topic :: Office/Business :: Groupware',
                     'Topic :: Utilities',
                     'Intended Audience :: System Administrators',
                     'Intended Audience :: End Users/Desktop',
                     'Intended Audience :: Science/Research',
                     'Intended Audience :: Education'],
    )


# Configure some of this at runtime.
def Summary():
    # Merge code package documentation and setup top-level.
    return __doc__ % dict(main_documentation = '')

def Configuration(packages):
    from mud import __version__

    # Overlay configuration:
    SETUP_CONF['version'] = __version__
    SETUP_CONF['url'] = __url__

    SETUP_CONF['author'] = __author__
    SETUP_CONF['author_email'] = __author_email__

    SETUP_CONF['long_description'] = Summary()
    SETUP_CONF['packages'] = packages

    return SETUP_CONF

def Setup():
    try: from setuptools import setup, find_packages
    except ImportError: from distutils.core import setup, find_packages

    # Invoke setup script:
    setup(**Configuration(find_packages()))

if __name__ == '__main__':
    Setup()

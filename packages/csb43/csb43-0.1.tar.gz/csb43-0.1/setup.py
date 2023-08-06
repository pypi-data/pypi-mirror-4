import os

from setuptools import setup, find_packages

import csb43


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top
# level README file and 2) it's easier to type in the README file than to put
# a raw string in below ...


def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as f:
            return f.read()
    except:
        return ''


config = {'name': "csb43",
          'version': csb43.__version__,
          'author': "wmj",
          'author_email' : "wmj.py@gmx.com",
          'description': csb43.__doc__,
          'license': "LGPL",
          'keywords': "csb csb43 homebank csv ofx Spanish bank",
          'url': "https://bitbucket.org/wmj/csb43",
          'packages': find_packages(),
          'long_description': read('_README.rst'),
          'scripts': ["csb2homebank", "csb2ofx"],
          'requires': ["pycountry"],
          'install_requires': ['pycountry'],
#          'test_requires': ['pycountry'],
          'test_suite': 'csb43.tests',
          'classifiers': ["Development Status :: 3 - Alpha",
                          "Environment :: Console",
                          "Topic :: Utilities",
			  "Topic :: Office/Business :: Financial",
			  "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
                          ]
          }


try:
    import py2exe

    config['console'] = ["csb2homebank", "csb2ofx"]
    config['options'] = {"py2exe": {"bundle_files": 1}}
    config['zipfile'] = None
except ImportError:
    pass


setup(**config)

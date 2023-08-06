import os

from setuptools import find_packages, setup

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

try:
    from babel.messages import frontend as babel

    entry_points = """
    [distutils.commands]
    compile_catalog = babel:compile_catalog
    extract_messages = babel:extract_messages
    init_catalog = babel:init_catalog
    update_catalog = babel:update_catalog
    """
except ImportError:
    pass

config = {'name': "csb43",
        'version': csb43.__version__,
        'author': "wmj",
        'author_email' : "wmj.py@gmx.com",
        'description': csb43.__doc__,
        'license': "LGPL",
        'keywords': "csb csb43 homebank ofx Spanish bank ods tsv xls xlsx excel yaml json html",
        'url': "https://bitbucket.org/wmj/csb43",
        'packages': find_packages(),
        'long_description': read('_README.rst')+read('INSTALL')+read('CHANGELOG'),
        'scripts': ["csb2homebank", "csb2ofx", "csb2format"],
        'requires': ["pycountry", "tablib", "PyYAML", "simplejson"],
        'install_requires': ["pycountry", "tablib", "PyYAML", "simplejson"],
        'include_package_data': True,
        'extras_require': {
            'babel': ["Babel"],
        },
        'test_suite': 'csb43.tests',
        #'package_data': {
            #'i18n': ['csb43/i18n/*']
        #},
        'classifiers': ["Development Status :: 3 - Alpha",
                        "Environment :: Console",
                        "Topic :: Utilities",
            "Topic :: Office/Business :: Financial",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
                        ],
        # distutils.commands en entry_points
        }


try:
    import py2exe

    config['console'] = ["csb2format", "csb2homebank", "csb2ofx"]
    config['options'] = {"py2exe": {"bundle_files": 1}}
    config['zipfile'] = None
except ImportError:
    pass


setup(**config)

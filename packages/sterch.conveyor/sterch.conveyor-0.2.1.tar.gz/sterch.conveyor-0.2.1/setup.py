### -*- coding: utf-8 -*- #############################################
# Developed by Maksym Polshcha (maxp@sterch.net)
# All right reserved, 2012
#######################################################################

"""setup script class for the ZTK-based sterch.conveyor package

"""
__author__  = "Polscha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def alltests():
    import logging
    import pkg_resources
    import unittest

    class NullHandler(logging.Handler):
        level = 50
        
        def emit(self, record):
            pass

    logging.getLogger().addHandler(NullHandler())

    suite = unittest.TestSuite()
    base = pkg_resources.working_set.find(
        pkg_resources.Requirement.parse('sterch.conveyor')).location
    for dirpath, dirnames, filenames in os.walk(base):
        if os.path.basename(dirpath) == 'tests':
            for filename in filenames:
                if filename.endswith('.py') and filename.startswith('test'):
                    mod = __import__(
                        _modname(dirpath, base, os.path.splitext(filename)[0]),
                        {}, {}, ['*'])
                    suite.addTest(mod.test_suite())
        elif 'tests.py' in filenames:
            continue
            mod = __import__(_modname(dirpath, base, 'tests'), {}, {}, ['*'])
            suite.addTest(mod.test_suite())
    return suite

setup( name='sterch.conveyor',
    version='0.2.1',
    url='http://pypi.sterch.net/sterch.conveyor',
    license='ZPL 2.1',
    description='Provides ZCML-based tools to define simultaneous tasks processing conveyors',
    author='Maksym Polscha',
    author_email='maxp@sterch.net',
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['sterch'],
    include_package_data=True,
    exclude_package_data = { '': ['.gitignore', 'bootstrap.py', 'buildout.cfg'] },
    install_requires=['setuptools',
                        'zope.interface',
                        'zope.schema',
                        'zope.cachedescriptors',
                        'zope.configuration',
                        'zope.component',
                        'sterch.threading',
                        'sterch.queue',
                        ],
    extras_require={'test': ['zope.testing'],},                        
    test_suite='__main__.alltests',
    tests_require=['zope.testing'],
    )
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os.path

from setuptools import setup, find_packages

def read(rel_path):
    rel_path = rel_path.split('/')
    base_path = os.path.dirname(__file__)
    path = (base_path,) + tuple(rel_path)
    return file(os.path.join(*path)).read()

setup(
    name = 'gocept.pagelet',
    version='0.4',
    author = "Christian Zagrodnick",
    author_email = "cz@gocept.com",
    description = "Easier z3c.pagelet handling",
    long_description = '\n\n'.join([
        read('README.txt'),
        read('CHANGES.txt'),
        read('src/gocept/pagelet/README.txt')]),
    license = "ZPL 2.1",
    url='http://pypi.python.org/pypi/gocept.pagelet',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    keywords = 'easy z3.pagelet zope3 pagelet zope',

    packages = find_packages('src'),
    package_dir = {'': 'src'},

    include_package_data = True,
    zip_safe = False,

    namespace_packages = ['gocept'],
    install_requires = [
        'setuptools',
        'zope.interface',
        'zope.component',
        'zope.publisher',
        'zope.viewlet',
        'z3c.template',
        'z3c.pagelet',
        'zope.browsermenu',
        'zope.browserpage',
        ],
    extras_require = dict(
        test=['zope.testing'])
    )

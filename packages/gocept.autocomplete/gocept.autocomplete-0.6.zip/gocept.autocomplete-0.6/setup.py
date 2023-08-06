# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


setup(
    name='gocept.autocomplete',
    version='0.6',
    author='gocept',
    author_email='mail@gocept.com',
    description='AJAX autocomplete widget for z3c.form',
    long_description = (
        open(os.path.join('src', 'gocept', 'autocomplete', 'README.txt')).read() +
        '\n\n' +
        open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=[
        'js.jqueryui',
        'setuptools',
        'z3c.form',
        'zope.browser',
        'zope.component',
        'zope.interface',
        'zope.pagetemplate',
        'zope.publisher',
        'zope.schema',
        'zope.traversing',
        ],
    extras_require=dict(
        test=[
            'lxml',
            'gocept.selenium',
            'zope.app.appsetup',
            'zope.app.testing',
            'zope.app.zcmlfiles',
            'zope.securitypolicy',
            'zope.server',
            'zope.app.server',
            'zope.testing',
            'zope.testbrowser>=3.4.3',
            ]),
)

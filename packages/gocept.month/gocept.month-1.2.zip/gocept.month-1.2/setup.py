# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='gocept.month',
    version='1.2',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    url='http://pypi.python.org/pypi/gocept.month',
    description="A datatype which stores a year and a month.",
    long_description= (
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages = ['gocept'],
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
    ],
    extras_require=dict(
        form=[
            'z3c.form',
            'zope.formlib >= 4.0',
        ],
        test=[
        'zope.app.pagetemplate',  # required by z3c.form which doesn't declare it
        'zope.testing',
        'zope.site',  # required by z3c.form which is too old to recognize zope.component.hooks
    ]),
)

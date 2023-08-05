# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages
import os.path

def read(*names):
    return open(
            os.path.join(os.path.dirname(__file__), *names)).read()

setup(
    name='gocept.linkchecker',
    version='3.0a9',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    description='Check links in your Plone site using a link monitoring server.',
    long_description=(
        read('src', 'gocept', 'linkchecker', 'doc', 'README.txt') +
        '\n\n' +
        read('CHANGES.txt')),
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=['setuptools', 'lxml'],
)

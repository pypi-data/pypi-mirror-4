# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.4.1'


def read(*rnames):

    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_maskmoney', 'test_jquery-maskmoney.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_maskmoney',
    version=version,
    description="Fanstatic packaging of jQuery-maskMoney",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/disko/js.jquery_maskmoney',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery-maskmoney = js.jquery_maskmoney:library',
            ],
        },
    )

# -*- coding: utf-8 -*-

import os
from setuptools import find_packages
from setuptools import setup

version = '1.3'


def read(*rnames):

    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_option_tree', 'test_jquery_option_tree.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_option_tree',
    version=version,
    description="Fanstatic packaging of jquery-option-tree",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    url='https://github.com/disko/js.jquery_option_tree',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery_option_tree = js.jquery_option_tree:library',
            ],
        },
    )

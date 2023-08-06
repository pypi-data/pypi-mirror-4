# -*- coding: utf-8 -*-

import os
from setuptools import find_packages
from setuptools import setup

version = '2.0-rc-2'


def read(*rnames):

    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'jquery_ui_multiselect2', 'test_jquery_ui_multiselect2.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.jquery_ui_multiselect2',
    version=version,
    description="Fanstatic packaging of jquery-ui-multiselect2",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    url='https://github.com/teixas/js.jquery_ui_multiselect2',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jqueryui',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jquery-ui-multiselect2 = js.jquery_ui_multiselect2:library',
            ],
        },
    )

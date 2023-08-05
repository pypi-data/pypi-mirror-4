import os

from setuptools import find_packages
from setuptools import setup

version = '1.2.2'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'dynatree', 'test_jquery.dynatree.js.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.dynatree',
    version=version,
    description="Fanstatic packaging of jquery.dynatree.js",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'js.jqueryui',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'jquery.dynatree.js = js.dynatree:library',
            ],
        },
    )

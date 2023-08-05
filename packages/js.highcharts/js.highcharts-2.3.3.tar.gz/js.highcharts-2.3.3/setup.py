import os

from setuptools import find_packages
from setuptools import setup

version = '2.3.3'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'highcharts', 'test_highcharts.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.highcharts',
    version=version,
    description="Fanstatic packaging of Highcharts",
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
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'highcharts = js.highcharts:library',
            ],
        },
    )

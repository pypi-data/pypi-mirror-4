import os
import sys

from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()
VERSION = '0.1'


setup(
    name='nose-knows',
    version=VERSION,
    classifiers=['License :: OSI Approved :: BSD License'],
    long_description=README + '\n\n' + NEWS,
    url='https://github.com/eventbrite/nose-knows',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'nose.plugins.0.10': ['knows = knows.nose_plugin:KnowsNosePlugin'],
        'pytest11': ['knows = knows.pytest_plugin'],
    },
)

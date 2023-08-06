import os
import re

from setuptools import setup
from setuptools import find_packages


NAME = 'pez'
PATH_TO_FILE = os.path.dirname(__file__)


def _get_version():
    path = os.path.join(PATH_TO_FILE, NAME, '__init__.py')
    version_re = r".*__version__ = '(.*?)'"
    fo = open(path)
    try:
        return re.compile(version_re, re.S).match(fo.read()).group(1)
    finally:
        fo.close()


def _get_long_description():
    path = os.path.join(PATH_TO_FILE, 'README.mkd')
    fo = open(path)
    try:
        return fo.read()
    finally:
        fo.close()


setup(
    name=NAME,
    version=_get_version(),
    description="PEZ - Python P(r)e-(Seriali)z(ation)",
    long_description=_get_long_description(),
    author='Balanced',
    author_email='dev@balancedpayments.com',
    url='https://github.com/balanced/pez',
    install_requires=[
    ],
    setup_requires=[],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    zip_safe=False,
    dependency_links = []
)

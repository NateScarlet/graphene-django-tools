"""Python setup script.  """
import os
import sys

from setuptools import find_packages, setup

NAME = 'graphene_django_tools'
REQUIRES = [
    'graphene-django~=2.2.0',
]

__about__ = {}
with open(os.path.join(os.path.dirname(__file__),
                       NAME, '__about__.py')) as f:
    exec(f.read(), __about__)  # pylint: disable=exec-used

setup(
    name=NAME,
    version=__about__['__version__'],
    author=__about__['__author__'],
    packages=find_packages(),
    package_data={},
    install_requires=REQUIRES
)

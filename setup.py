"""Python setup script.  """
import os
import re

from setuptools import find_packages, setup

NAME = 'graphene_django_tools'
REQUIRES = [
    'graphene-django~=2.2.0',
    'isodate~=0.6.0'
]

__about__ = {}
with open(os.path.join(os.path.dirname(__file__),
                       NAME, '__about__.py')) as f:
    exec(f.read(), __about__)  # pylint: disable=exec-used


def _get_long_description():
    with open(os.path.join(os.path.dirname(__file__),
                           "README.md"), "r") as f:
        return re.sub(r'(\[.*\]\()\./',
                      lambda matches:
                      (matches[1] +
                       'https://github.com/NateScarlet/graphene-django-tools'
                       '/blob/{}/'.format(__about__['__version__'])),
                      f.read())


setup(
    name=NAME,
    version=__about__['__version__'],
    author=__about__['__author__'],
    author_email=__about__['__author__'],
    url='https://github.com/NateScarlet/graphene-django-tools',
    packages=find_packages(),
    package_data={},
    install_requires=REQUIRES,
    description='Tools for use [graphene-django](https://github.com/graphql-python/graphene-django)',
    long_description=_get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=['Framework :: Django :: 2.1',
                 'Framework :: Django :: 2.2',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],
)

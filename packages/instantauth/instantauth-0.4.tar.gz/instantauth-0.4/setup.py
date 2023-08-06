from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    with open('instantauth/version.txt') as f:
        return f.read().strip()


def get_readme():
    try:
        with open('README.rst') as f:
            return f.read().strip()
    except IOError:
        return ''

setup(
    name='instantauth',
    version=get_version(),
    description='Not very credential authentication model.',
    long_description=get_readme(),
    author='Jeong YunWon',
    author_email='jeong+instantauth@youknowone.org',
    url='https://github.com/youknowone/instantauth',
    packages=(
        'instantauth',
        'instantauth/cryptors',
        'instantauth/verifiers',
        'instantauth/coders',
    ),
    package_data={
        'instantauth': ['version.txt']
    },
    install_requires=[
        'distribute',
    ],
)
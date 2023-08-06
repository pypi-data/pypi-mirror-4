"""
virtstrap-core
==============

A bootstrapping mechanism for virtualenv, buildout, and shell scripts.
"""
from setuptools import setup, find_packages

VERSION = '0.3.14'

# Installation requirements
REQUIREMENTS = []

setup(
    name="virtstrap-core",
    version=VERSION,
    license="MIT",
    author="Reuven V. Gonzales",
    url="https://github.com/ravenac95/virtstrap-core",
    author_email="reuven@tobetter.us",
    description="A bootstrapping mechanism for virtualenv+pip and shell scripts",
    long_description="virtstrap-core is not meant to be installed manually",
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    platforms='*nix',
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'virtstrap-tempfiler = virtstrap.tempfiler:main',
        ],
    },
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Software Development :: Build Tools',
    ],
)

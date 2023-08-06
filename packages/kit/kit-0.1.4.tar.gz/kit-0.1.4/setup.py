#!/usr/bin/env python

from setuptools import find_packages, setup

def get_version():
  from kit import __version__
  return __version__

setup(
    name='kit',
    version=get_version(),
    description='Flask, Celery, SQLAlchemy integration toolkit',
    long_description=open('README.rst').read(),
    author='Matthieu Monsch',
    author_email='monsch@mit.edu',
    url='http://github.com/mtth/kit/',
    license='MIT',
    packages=find_packages(),
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
    ],
    install_requires=[
      'blinker',
      'pyyaml',
    ],
    entry_points={'console_scripts': ['kit = kit.__main__:main']},
)

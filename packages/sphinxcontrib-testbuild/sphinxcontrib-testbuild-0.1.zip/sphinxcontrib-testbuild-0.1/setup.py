# -*- coding: utf-8 -*-
from os.path import dirname, join
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(join(dirname(__file__), filename)) as f:
        return f.read().strip()


name = 'sphinxcontrib-testbuild'
packages = ['sphinxcontrib.testbuild']
readme = read_relative_file('README')
version = read_relative_file('VERSION')
requirements = ['setuptools']
entry_points = {}


if __name__ == '__main__':
    setup(name=name,
          version=version,
          description='Test Sphinx builds with Python tests.',
          long_description=readme,
          author='Benoît Bryon',
          author_email='benoit@marmelune.net',
          url='https://bitbucket.org/benoitbryon/sphinxcontrib-testbuild',
          license='BSD',
          zip_safe=False,
          classifiers=['Development Status :: 4 - Beta',
                       'Environment :: Console',
                       'Environment :: Web Environment',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Topic :: Documentation',
                       'Topic :: Utilities',
                       ],
          platforms='any',
          packages=packages,
          namespace_packages=['sphinxcontrib'],
          include_package_data=True,
          install_requires=requirements,
          entry_points=entry_points,
          )

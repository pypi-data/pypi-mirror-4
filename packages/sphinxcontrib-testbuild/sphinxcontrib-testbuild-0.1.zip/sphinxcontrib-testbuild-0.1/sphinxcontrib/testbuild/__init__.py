# -*- coding: utf-8 -*-
"""Test Sphinx builds with Python tests."""
pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('sphinxcontrib-testbuild')

#: Module version, as defined in PEP-0396.
__version__ = distribution.version

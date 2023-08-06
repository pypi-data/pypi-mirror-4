"""Test integration for ``adapter.txt``.

This integrates the doctests in file ``adapter.txt`` into
the Zope testrunner framework.
"""
from zope.testing.doctest import DocFileSuite

def test_suite():
  return DocFileSuite('adapter.txt',
                      module_relative=True,
                      )

##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test setup for Base setting UI tests.

$Id: ftests.py 112974 2010-06-03 06:57:11Z ctheune $
"""
__docformat__ = "reStructuredText"
import unittest
import zope.component
import zope.interface
from zope.app.testing.functional import FunctionalDocFileSuite

from z3c.baseregistry import baseregistry


custom = baseregistry.BaseComponents(
    zope.component.globalSiteManager, 'custom')


class IExample(zope.interface.Interface):
    name = zope.interface.Attribute('Name of Example')

class Example(object):
    zope.interface.implements(IExample)
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)

example1 = Example('example1')
example2 = Example('example2')
example3 = Example('example3')
example4 = Example('example4')


def addBasesSelection(browser, bases):
    # Get the form
    form = browser.mech_browser.forms().next()
    select_attrs = {'name': 'form.__bases__', 'size': '5',
                    'multiple': 'multiple'}
    # Create the select tag
    form.new_control(
        'select', 'form.__bases__',
        attrs={'__select': select_attrs})
    # Add options
    for idx, base in enumerate(bases):
        form.new_control(
            'select', 'form.__bases__',
            attrs={'__select': select_attrs,
                   'selected': 'selected',
                   'value': base},
            index=idx
            )


def test_suite():
    suite = unittest.TestSuite((
        FunctionalDocFileSuite(
            'README.txt',
            globs={'IExample': IExample,
                   'addBasesSelection': addBasesSelection}),
        ))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

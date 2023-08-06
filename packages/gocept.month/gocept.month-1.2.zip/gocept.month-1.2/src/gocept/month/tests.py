# Copyright (c) 2005-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import date
from doctest import DocTestSuite
from gocept.month.adapter import Date, BuiltinStr
from gocept.month.interfaces import IDate, IMonth
import unittest
import zope.component
import zope.interface


class Layer(object):

    __name__ = 'gocept.month.layer'
    __bases__ = ()

    def setUp(self):
        zope.interface.classImplements(date, IDate)
        zope.component.provideAdapter(Date, (IDate,), IMonth)
        zope.component.provideAdapter(BuiltinStr, (str,), IMonth)

    def tearDown(self):
        zope.component.getSiteManager().unregisterAdapter(
            Date, (IDate,), IMonth)
        zope.component.getSiteManager().unregisterAdapter(
            BuiltinStr, (str,), IMonth)

layer = Layer()


def test_suite():
    suite = unittest.TestSuite((
        DocTestSuite('gocept.month._month'),
        DocTestSuite('gocept.month.field'),
        DocTestSuite('gocept.month.browser.widget'),
        DocTestSuite('gocept.month.interval'),
        DocTestSuite('gocept.month.adapter'),
        ))
    suite.layer = layer
    return suite

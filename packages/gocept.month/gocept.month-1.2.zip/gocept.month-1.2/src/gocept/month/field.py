# Copyright (c) 2005-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.month import Month
from gocept.month.interfaces import IMonthField
import zope.schema
import zope.interface


class MonthField(zope.schema.Orderable, zope.schema.Field):
    """Field containing a Month.

    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(IMonthField, MonthField())
    True
    """

    zope.interface.implements(IMonthField, zope.schema.interfaces.IFromUnicode)

    _type = Month

    def fromUnicode(self, str):
        return Month.fromString(str)

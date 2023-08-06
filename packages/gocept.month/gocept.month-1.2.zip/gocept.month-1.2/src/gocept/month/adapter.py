# Copyright (c) 2005-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.month import Month


def Date(date):
    """Adapter between Date and Month.

    >>> from datetime import date
    >>> from zope.interface.verify import verifyObject
    >>> from gocept.month import IMonth

    >>> today = date.today()
    >>> verifyObject(IMonth, Date(today))
    True
    >>> Date(today).month == today.month
    True
    >>> Date(today).year == today.year
    True
    >>> Date(date(2005,12,06))
    Month 12/2005
    >>> str(Date(date(2005,12,06)))
    '12/2005'
    >>> str(Date(date(2005,12,06)) + 1)
    '01/2006'
    >>> Date(today) > Month(today.month, today.year-1)
    True
    >>> Date(today) == Month(today.month, today.year)
    True
    """
    return Month(date.month, date.year)


def BuiltinStr(date):
    return Month.fromString(date)

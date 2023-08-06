# Copyright (c) 2005-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.month.interfaces import IMonth
import datetime
import gocept.month
import re
import zope.interface


class Month(object):
    """A datatype which stores a year and a month.

    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(IMonth, Month(11, 1977))
    True
    """

    zope.interface.implements(IMonth)

    month = property(lambda self: self.__month)
    year = property(lambda self: self.__year)

    def __init__(self, month, year):
        """Constructor

        >>> Month()
        Traceback (most recent call last):
        ...
        TypeError: __init__() takes exactly 3 arguments (1 given)
        >>> Month(13,2005)
        Traceback (most recent call last):
        ...
        ValueError: Month must be between 1 and 12.
        >>> Month(0,2005)
        Traceback (most recent call last):
        ...
        ValueError: Month must be between 1 and 12.
        >>> Month(11,2005)
        Month 11/2005
        >>> Month(11,5)
        Month 11/5
        >>> Month(11,99)
        Month 11/99
        >>> Month(11,-20)
        Traceback (most recent call last):
        ...
        ValueError: Year must be at least 1.
        """
        month = int(month)
        if not(1 <= month <= 12):
            raise ValueError('Month must be between 1 and 12.')
        self.__month = month

        year = int(year)
        if year <= 0:
            raise ValueError("Year must be at least 1.")
        self.__year = year

    def __repr__(self):
        return "Month %s/%s" % (self.month, self.year)

    def __cmp__(self, other):
        """Compare to other.
        If other is not adaptable to IMonth it is always less than self.

        >>> m1 = Month(11,2005)
        >>> cmp(m1, None)
        1
        >>> cmp(m1, Month(11,2005))
        0
        >>> cmp(m1, Month(12,2005))
        -1
        >>> cmp(m1, Month(10,2005))
        1
        >>> cmp(m1, Month(11,2006))
        -1
        >>> cmp(m1, Month(11,2004))
        1

        >>> m1 == None
        False
        >>> m1 == Month(11,2005)
        True
        >>> m1 == Month(10,2005)
        False
        >>> m1 == Month(11,2004)
        False

        >>> m1 >= None
        True
        >>> m1 >= Month(11,2005)
        True
        >>> m1 >= Month(12,2005)
        False
        >>> m1 >= Month(10,2005)
        True
        >>> m1 >= Month(11,2004)
        True
        >>> m1 >= Month(11,2006)
        False
        >>> m1 >= Month(12,2006)
        False
        >>> m1 >= Month(12,2004)
        True

        >>> m1 > None
        True
        >>> m1 > Month(11,2005)
        False
        >>> m1 > Month(12,2005)
        False
        >>> m1 > Month(10,2005)
        True
        >>> m1 > Month(11,2004)
        True
        >>> m1 > Month(11,2006)
        False
        >>> m1 > Month(12,2006)
        False
        >>> m1 > Month(12,2004)
        True

        >>> m1 < None
        False
        >>> m1 <= None
        False
        >>> m1 != None
        True

        We allow comparison with months that are a string too:

        >>> m1 > "11/2005"
        False
        >>> m1 > "12/2005"
        False
        >>> m1 == "11/2005"
        True
        >>> m1 < "12/2005"
        True
        """
        try:
            other = IMonth(other)
        except TypeError:
            return 1
        else:
            return cmp(self.year, other.year) or cmp(self.month, other.month)

    def isBetween(self, a, b):
        """Check if the month is between a and b.

        DEPRECATED: Use `month in month_interval` instead.

        >>> m1 = Month(01,2001)
        >>> m2 = Month(01,2005)
        >>> m3 = Month(05,2005)
        >>> m2.isBetween(m1, m3)
        True
        >>> m2.isBetween(None, None)
        True
        >>> m2.isBetween(None, m1)
        False
        >>> m2.isBetween(None, m2)
        True
        >>> m2.isBetween(None, m3)
        True
        >>> m2.isBetween(m1, None)
        True
        >>> m2.isBetween(m2, None)
        True
        >>> m2.isBetween(m3, None)
        False
        >>> m1.isBetween(m2, m3)
        False
        >>> m1.isBetween(m1, m2)
        True
        >>> m1.isBetween(['wrong'], m2)
        Traceback (most recent call last):
        ...
        TypeError: ('Could not adapt', ['wrong'], <InterfaceClass gocept.month.interfaces.IMonth>)
        >>> m1.isBetween(m2, ['wrong'])
        Traceback (most recent call last):
        ...
        TypeError: ('Could not adapt', ['wrong'], <InterfaceClass gocept.month.interfaces.IMonth>)
        """
        if a is not None:
            a = IMonth(a)
        if b is not None:
            b = IMonth(b)

        return a <= self and (self <= b or b is None)

    date_regex = re.compile(r"^([0-9]{1,2})[,./-]?([0-9]{2}|[0-9]{4})$")

    @classmethod
    def current(cls):
        """Return a month instance for the current month.

        >>> Month.current() # doctest: +ELLIPSIS
        Month .../...

        """
        now = datetime.date.today()
        return Month(now.month, now.year)

    @classmethod
    def fromString(cls, string):
        """Get instance from a string. The Month must come first in string.

        >>> Month.fromString('11/2005')
        Month 11/2005
        >>> Month.fromString('11.2005')
        Month 11/2005
        >>> Month.fromString('11-2005')
        Month 11/2005
        >>> Month.fromString('11.2005')
        Month 11/2005
        >>> Month.fromString('1.2005')
        Month 1/2005
        >>> Month.fromString('01.2005')
        Month 1/2005
        >>> Month.fromString('11.05')
        Month 11/2005
        >>> Month.fromString('11/05')
        Month 11/2005
        >>> Month.fromString('1105')
        Month 11/2005
        >>> Month.fromString('112005')
        Month 11/2005
        >>> Month.fromString('105')
        Month 1/2005
        >>> Month.fromString('12005')
        Month 1/2005
        >>> Month.fromString('0105')
        Month 1/2005
        >>> Month.fromString('0501')
        Month 5/2001
        >>> Month.fromString('012005')
        Month 1/2005

        Empty strings result in None instead of a Month instance

        >>> Month.fromString('') is None
        True

        Format Errors result in a ValueError

        >>> Month.fromString('2005-11')
        Traceback (most recent call last):
        ...
        ValueError: Date must be MM/YYYY.
        """
        if string == '':
            return None
        result = cls.date_regex.match(string)
        if result is None:
            raise ValueError('Date must be MM/YYYY.')
        month, year = result.groups()
        if len(year) == 2:
            year = "20%s" % year
        return Month(int(month), int(year))

    def firstOfMonth(self):
        """Get the datetime.date which represents the first day of the month.

        >>> Month(11, 2005).firstOfMonth()
        datetime.date(2005, 11, 1)
        >>> Month(1, 2000).firstOfMonth()
        datetime.date(2000, 1, 1)
        """
        return datetime.date(self.year, self.month, 1)

    def lastOfMonth(self):
        """Get the datetime.date which represents the last day of the month.

        >>> Month(11, 2005).lastOfMonth()
        datetime.date(2005, 11, 30)
        >>> Month(12, 2005).lastOfMonth()
        datetime.date(2005, 12, 31)
        >>> Month(2, 2008).lastOfMonth()
        datetime.date(2008, 2, 29)
        """
        next_month = self + 1
        return next_month.firstOfMonth() - datetime.timedelta(days=1)

    def __sub__(self, other):
        """Substract from this month.

        Given an `int` a previous month is computed:

        >>> Month(11, 2005) - 10
        Month 1/2005
        >>> Month(1, 2005) - 13
        Month 12/2003
        >>> Month(1, 2005) - 5
        Month 8/2004

        Given an `IMonth` an interval is computed:

        >>> Month(11, 2005) - Month(1, 2005)
        <MonthInterval from Month 11/2005 to Month 1/2005>
        >>> Month(1, 2005) - Month(11, 2005)
        <MonthInterval from Month 1/2005 to Month 11/2005>

        Trying to substract other types raises an error:
        >>> Month(11, 2005) - '1'
        Traceback (most recent call last):
        TypeError: Can't substract <type 'str'> from month.

        """
        if isinstance(other, int):
            months = other
            year = self.year - (months / 12)
            month = self.month - months % 12
            if month <= 0:
                year -= 1
                month += 12
            return Month(month, year)
        elif IMonth.providedBy(other):
            return gocept.month.MonthInterval(self, other)
        raise TypeError("Can't substract %r from month." % type(other))

    def __add__(self, months):
        """Add months and return a new IMonth.

        >>> m1 = Month(12,2005)
        >>> m2 = Month(1,2005)
        >>> m1 + 1
        Month 1/2006
        >>> m2 + 1
        Month 2/2005
        >>> m2 + 13
        Month 2/2006
        """
        return self - (-months)

    def __str__(self):
        """Returns a string representation.

        >>> str(Month(10,2000))
        '10/2000'
        >>> str(Month(1,2005))
        '01/2005'
        """
        return "%02i/%s" % (self.month, self.year)

    def __hash__(self):
        """Returns the hash.

        Make sure Month is immutable:

        >>> Month(5,2003).year = 2005
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute
        >>> Month(5,2003).month = 4
        Traceback (most recent call last):
        ...
        AttributeError: can't set attribute

        Check the hash

        >>> hash(Month(10,2000))
        102000
        >>> hash(Month(1,2005))
        12005
        >>>
        """
        return int("%s%s" % (self.month, self.year))

    def __iter__(self):
        """Returns an iterator over the days of the month.

        Represents each day as a datetime.date.

        >>> days = iter(Month(05, 2009))
        >>> days.next()
        datetime.date(2009, 5, 1)
        >>> days.next()
        datetime.date(2009, 5, 2)
        >>> for day in days: pass
        >>> day
        datetime.date(2009, 5, 31)

        """
        return (datetime.date(self.year, self.month, day)
                for day in range(1, self.lastOfMonth().day + 1))

    def __contains__(self, date):
        """Returns whether the `date` is in the month.

        >>> import datetime
        >>> datetime.date(2009, 4, 30) in Month(5, 2009)
        False
        >>> datetime.date(2009, 5, 1) in Month(5, 2009)
        True
        >>> datetime.date(2009, 5, 2) in Month(5, 2009)
        True
        >>> datetime.date(2009, 5, 31) in Month(5, 2009)
        True
        >>> datetime.date(2009, 6, 1) in Month(5, 2009)
        False
        >>> datetime.date(2012, 2, 29) in Month(2, 2012)
        True
        >>> datetime.datetime(2012, 2, 29, 15, 7, 34) in Month(2, 2012)
        True
        >>> object() in Month(2, 2012)
        False

        """
        if not isinstance(date, datetime.date):
            return False
        return date.year == self.year and date.month == self.month

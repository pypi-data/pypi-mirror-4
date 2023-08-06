# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.month import IMonthInterval, IMonth, Month
import gocept.month
import zope.interface


class MonthInterval(object):
    """represents a month interval
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IMonthInterval, MonthInterval)
    True
    """

    zope.interface.implements(IMonthInterval)

    start = None
    end = None

    def __init__(self, start, end):
        """Create an interval between start and end.

        Start and end must be months:

        >>> from gocept.month import Month
        >>> MonthInterval(1,2)
        Traceback (most recent call last):
        TypeError: start 1 is not a month.
        >>> MonthInterval(Month(1, 2012), Month(3, 2012))
        <MonthInterval from Month 1/2012 to Month 3/2012>

        Alternatively None can be given to indicate open intervals:

        >>> MonthInterval(None, Month(3, 2012))
        <MonthInterval from Month 1/1 to Month 3/2012>
        >>> MonthInterval(Month(2, 2005), None)
        <MonthInterval from Month 2/2005 to Month 12/9999>

        Reverse intervals are also supported:

        >>> MonthInterval(Month(3, 2012), Month(1, 2012))
        <MonthInterval from Month 3/2012 to Month 1/2012>

        """
        if start is None:
            start = gocept.month.Month(1, 1)
        if end is None:
            end = gocept.month.Month(12, 9999)

        if not IMonth.providedBy(start):
            raise TypeError("start %r is not a month." % start)
        if not IMonth.providedBy(end):
            raise TypeError("end %r is not a month." % end)

        self.start = start
        self.end = end

    def __repr__(self):
        return '<MonthInterval from %r to %r>' % (self.start, self.end)

    def __iter__(self):
        """Iterate over all months that are in the interval, including start
        and end.

        >>> from gocept.month import Month
        >>> for m in MonthInterval(Month(1, 2005), Month(12, 2005)):
        ...     print m
        01/2005
        02/2005
        03/2005
        04/2005
        05/2005
        06/2005
        07/2005
        08/2005
        09/2005
        10/2005
        11/2005
        12/2005

        >>> for m in MonthInterval(Month(11, 2005), Month(9, 2005)):
        ...     print m
        11/2005
        10/2005
        09/2005

        >>> list(MonthInterval(Month(11, 2005), Month(11, 2005)))
        [Month 11/2005]

        >>> open_interval = MonthInterval(Month(11, 2005), None)
        >>> i = iter(open_interval)
        >>> print i.next()
        11/2005
        >>> print i.next()
        12/2005

        >>> open_interval = MonthInterval(None, Month(11, 2005))
        >>> i = iter(open_interval)
        >>> print i.next()
        01/1
        >>> print i.next()
        02/1

        """
        if self.start <= self.end:
            op = +1
        else:
            op = -1

        month = self.start
        while True:
            yield month
            if month == self.end:
                return
            month += op

    def intersects(self, other):
        """Check whether this interval shares months with another interval.

        >>> from gocept.month import Month
        >>> i = MonthInterval(Month(12, 4), Month(6, 5))
        >>> i.intersects(4)
        Traceback (most recent call last):
        ...
        TypeError: Not an interval: 4
        >>> i.intersects(MonthInterval(Month(5, 5), Month(7, 5)))
        True
        >>> i.intersects(MonthInterval(Month(6, 5), Month(8, 5)))
        True
        >>> i.intersects(MonthInterval(Month(7, 5), Month(9, 5)))
        False
        >>> i.intersects(MonthInterval(Month(11, 4), Month(1, 5)))
        True
        >>> i.intersects(MonthInterval(Month(10, 4), Month(12, 4)))
        True
        >>> i.intersects(MonthInterval(Month(9, 4), Month(11, 4)))
        False
        >>> i.intersects(MonthInterval(Month(2, 5), Month(04, 5)))
        True
        >>> i.intersects(i)
        True
        >>> i.intersects(MonthInterval(Month(9, 4), Month(3, 5)))
        True
        >>> i.intersects(MonthInterval(Month(3, 5), Month(9, 5)))
        True
        >>> MonthInterval(Month(9, 4), Month(9, 5)).intersects(i)
        True
        >>> i.intersects(MonthInterval(Month(9, 4), Month(9, 5)))
        True
        >>> i.intersects(MonthInterval(None, None))
        True
        >>> MonthInterval(None, None).intersects(MonthInterval(None, None))
        True
        >>> i.intersects(MonthInterval(None, Month(1, 5)))
        True
        >>> MonthInterval(None, Month(12, 4)).intersects(i)
        True
        >>> i.intersects(MonthInterval(None, Month(12, 4)))
        True
        >>> i.intersects(MonthInterval(None, Month(11, 4)))
        False
        >>> i.intersects(MonthInterval(Month(5, 5), None))
        True
        >>> i.intersects(MonthInterval(Month(6, 5), None))
        True
        >>> MonthInterval(Month(7, 5), None).intersects(i)
        False
        >>> i.intersects(MonthInterval(Month(7, 5), None))
        False

        Intersection also works with reverse intervals:

        >>> i.intersects(MonthInterval(Month(7, 5), Month(3, 5)))
        True

        """
        if not IMonthInterval.providedBy(other):
            raise TypeError("Not an interval: %r" % other)
        a = self.normalized()
        b = other.normalized()
        if b.end < a.start:
            return False
        if a.end < b.start:
            return False
        return True

    def __contains__(self, month):
        """Returns true if the given month is within the interval.

        >>> from gocept.month import Month
        >>> interval = MonthInterval(Month(1, 2001), Month(5, 2001))
        >>> Month(1, 2001) in interval
        True
        >>> Month(5, 2001) in interval
        True
        >>> Month(3, 2001) in interval
        True
        >>> Month(12, 2000) in interval
        False
        >>> Month(6, 2001) in interval
        False
        >>> Month(10, 1999) in interval
        False
        >>> Month(10, 2007) in interval
        False

        Also works for reverse intervals:

        >>> Month(5, 2003) in MonthInterval(Month(10, 2003), Month(3, 2003))
        True

        """
        a = self.normalized()
        if a.start <= month <= a.end:
            return True
        return False

    def normalized(self):
        """Create a normalized form of this interval.

        >>> from gocept.month import Month
        >>> interval = MonthInterval(Month(5, 2001), Month(1, 2001))
        >>> interval.normalized()
        <MonthInterval from Month 1/2001 to Month 5/2001>
        >>> interval.normalized().normalized()
        <MonthInterval from Month 1/2001 to Month 5/2001>

        """
        if self.start <= self.end:
            start, end = self.start, self.end
        else:
            start, end = self.end, self.start
        return MonthInterval(start, end)

    @classmethod
    def forYear(cls, year):
        """Returns an interval of months for the given year.

        >>> MonthInterval.forYear(2001)
        <MonthInterval from Month 1/2001 to Month 12/2001>
        """
        return cls(Month(1, year), Month(12, year))

# coding: utf-8
# Copyright (c) 2005-2009, 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.month import Month
from zope.formlib.textwidgets import escape, TextWidget
from zope.formlib.widget import DisplayWidget, renderElement
from zope.formlib.interfaces import IDisplayWidget, IInputWidget, ConversionError
import gocept.month.field
import z3c.form.error
import zope.component
import zope.i18nmessageid
import zope.interface

_ = zope.i18nmessageid.MessageFactory("gocept")


class MonthConversionError(ConversionError):
    __doc__ = _(u"Format muss MM/JJJJ sein (z.B. 11/2005 für November 2005).")

    def doc(self):
        return self.__class__.__doc__


class MonthDisplayWidget(DisplayWidget):
    """Widget displaying the contents of an IMonthField."""

    zope.interface.implements(IDisplayWidget)

    cssClass = "month"

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if content == self.context.missing_value:
            return ""
        content = str(content)
        return renderElement("span",
                             contents=escape(content),
                             cssClass=self.cssClass)


class MonthEditWidget(TextWidget):
    """Widget displaying the contents of an IMonthField. """

    zope.interface.implements(IInputWidget)

    def _toFieldValue(self, input):
        try:
            return Month.fromString(input)
        except ValueError, error:
            raise MonthConversionError(error)


class MonthErrorViewSnippet(z3c.form.error.ErrorViewSnippet):

    zope.component.adapts(
        ValueError, None, None, gocept.month.field.MonthField, None,
        None)

    def createMessage(self):
        return MonthConversionError.__doc__

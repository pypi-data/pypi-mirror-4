##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
"""Tests for cipher.lazydate"""
import doctest
import datetime

from zope.interface.verify import verifyObject
from zope.component import hooks
from cipher.lazydate import lazydate, interfaces

def stub_now():
    return datetime.datetime(2001, 1, 1, 1, 1, 1)

def doctest_LazyDate():
    """LazyDate fulfills its interface.

        >>> lazy = lazydate.LazyDate("now")
        >>> verifyObject(interfaces.ILazyDate, lazy)
        True

    String representations returns the stored string:

        >>> print lazy
        now

        >>> lazy
        LazyDate('now')

    """


def doctest_LazyDate_fixed_date():
    """Lazy date accepts fixed date formats

    It does accept the US format:

        >>> lazy = lazydate.LazyDate("01/02/03")
        >>> print lazy.date()
        2003-01-02 00:00:00

    It assumes a US format even with the dots:

        >>> lazy = lazydate.LazyDate("11.12.13")
        >>> print lazy.date()
        2013-11-12 00:00:00

    ISO-format is now properly handled.

        >>> lazy = lazydate.LazyDate("2012-12-13")
        >>> lazy._now = stub_now
        >>> print lazy.datetime()
        2012-12-13 00:00:00

     """


def doctest_LazyDate_relative_date():
    """Lazy date accepts human descriptions

        >>> lazy = lazydate.LazyDate("today")
        >>> lazy._now = stub_now
        >>> print lazy.datetime()
        2001-01-01 09:00:00

        >>> lazy = lazydate.LazyDate("1 week later")
        >>> lazy._now = stub_now
        >>> print lazy.datetime()
        2001-01-08 01:01:01

        >>> lazy = lazydate.LazyDate("2 months ago at 3pm")
        >>> lazy._now = stub_now
        >>> print lazy.datetime()
        2000-11-01 15:00:00

        >>> lazy = lazydate.LazyDate("last friday")
        >>> lazy._now = stub_now
        >>> print lazy.datetime()
        2000-12-29 09:00:00

    """


def doctest_LazyDate_validate():
    """LazyDate knows if the string is valid or not:

        >>> lazy = lazydate.LazyDate("friday")
        >>> lazy.validate()
        True

        >>> lazy = lazydate.LazyDate("01/01")
        >>> lazy.validate()
        True

        >>> lazy = lazydate.LazyDate("now")
        >>> lazy.validate()
        True

        >>> lazy = lazydate.LazyDate("whenever")
        >>> lazy.validate()
        False

    dateutil.parser is very nice and accepts integers as a simple year.

        >>> lazy = lazydate.LazyDate("12")
        >>> lazy.validate()
        True

    """


def doctest_LazyDateField():
    """LazyDateField is a field for LazyDate values.

       >>> field = lazydate.LazyDateField(title=u"Date")
       >>> field.validate(lazydate.LazyDate("tomorrow"))

       >>> field.validate("01/01/01")
       Traceback (most recent call last):
         ...
       SchemaNotProvided

       >>> field.validate(datetime.date(2011, 1, 1))
       Traceback (most recent call last):
         ...
       SchemaNotProvided

    """


def doctest_LazyDateField_fromUnicode():
    """LazyDateField can convert strings to LazyDates

    LazyDateField needs active site to get timezone from

       >>> field = lazydate.LazyDateField(title=u"Date")
       >>> field.fromUnicode("tomorrow")
       LazyDate('tomorrow')

    For invalid values, it raises a ValueError:

       >>> field.fromUnicode(None)
       Traceback (most recent call last):
         ...
       ValueError: None

       >>> field.fromUnicode(u'42x')
       Traceback (most recent call last):
         ...
       ValueError: 42x

    """

def test_suite():
    return doctest.DocTestSuite(
        optionflags=doctest.REPORT_NDIFF|doctest.ELLIPSIS,
        )

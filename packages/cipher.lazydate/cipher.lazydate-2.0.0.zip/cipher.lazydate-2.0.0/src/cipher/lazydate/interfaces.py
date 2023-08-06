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
"""Interfaces for cipher.lazydate"""
import zope.interface
import zope.schema.interfaces


class ILazyDate(zope.interface.Interface):
    """A value object for a textual datetime specification.

    We want to resolve date specs such as "1 month ago" or "tomorrow"
    when they are being used, but also we want to accept concrete
    dates such as "01/02/03" of "2012-01-01".
    """
    def datetime():
        """Return the datetime of the date spec relative to now"""

    def date():
        """Return the date stored relative to now"""

    def validate():
        """Return if the stored date value is valid or not"""

    def __str__():
        """Return the stored date spec string"""


class ILazyDateField(zope.schema.interfaces.IObject,
                     zope.schema.interfaces.IFromUnicode):
    """Lazy date schema field"""

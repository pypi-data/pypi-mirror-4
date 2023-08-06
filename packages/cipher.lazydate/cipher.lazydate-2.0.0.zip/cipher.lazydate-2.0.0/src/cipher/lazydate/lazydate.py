###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""Lazy date field"""

import datetime
import dateutil.parser
import zope.interface
import zope.schema

from cipher.lazydate import interfaces
import cipher.lazydate.parsedatetime.parsedatetime
import cipher.lazydate.parsedatetime.parsedatetime_consts


@zope.interface.implementer(interfaces.ILazyDate)
class LazyDate(object):
    """A value object for a textual datetime specification."""

    def __init__(self, date):
        self.spec = str(date)

    def datetime(self):
        timetuple, result = self._parse()
        if not timetuple:
            return None
        dt = datetime.datetime(*timetuple[:6])
        return self._addTimeZone(dt)

    def date(self):
        timetuple, result = self._parse()
        if not timetuple:
            return None
        dt = datetime.datetime(*timetuple[:3])
        return self._addTimeZone(dt)

    def validate(self):
        timetuple, status = self._parse()
        return status != 0

    def _addTimeZone(self, dt):
        """A hook for subclasses to add timezone information for parsed dates"""
        return dt

    def _parse(self):
        # Try dateutil.parser first, since it does a better job with real
        # dates.
        if not self.spec:
            return None, 0

        try:
            dt = dateutil.parser.parse(self.spec)
        except ValueError:
            pass
        else:
            return dt.timetuple(), 1
        parser = cipher.lazydate.parsedatetime.parsedatetime.Calendar(
            cipher.lazydate.parsedatetime.parsedatetime_consts.Constants())
        # Now without timezone information because some expressions
        # are not parsed correctly for timezone-aware times.
        return parser.parse(self.spec, self._tzNaiveNow())

    def _now(self):
        return datetime.datetime.now()

    def _tzNaiveNow(self):
        """A hook for tz-aware subclasses"""
        return self._now().replace(tzinfo=None)

    def __str__(self):
        return self.spec

    def __repr__(self):
        return 'LazyDate(%r)' % (self.spec, )


@zope.interface.implementer(interfaces.ILazyDateField)
class LazyDateField(zope.schema.Object):
    """Lazy date schema field"""

    valueFactory = LazyDate

    def __init__(self, **kw):
        zope.schema.Object.__init__(self, interfaces.ILazyDate, **kw)

    def fromUnicode(self, strvalue):
        if strvalue == '':
            return None

        value = self.valueFactory(strvalue)
        if not value.validate():
            raise ValueError(strvalue)
        self.validate(value)
        return value

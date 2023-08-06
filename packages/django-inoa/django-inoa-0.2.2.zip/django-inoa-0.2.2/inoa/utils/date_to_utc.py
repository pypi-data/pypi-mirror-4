# -*- coding: utf-8 -*-
import calendar
import datetime

def date_to_utc(date):
    """
    Returns the UTC (Coordinated Universal Time) format of date.
    The date parameter must be a date or datetime instance.
    """
    if isinstance(date, datetime.date):
        utc_date = datetime.datetime.combine(date, datetime.time())
    elif isinstance(date, datetime.datetime):
        utc_date = date
    else:
        raise TypeError, u"date parameter must be a date or datetime instance"
    return calendar.timegm(utc_date.utctimetuple()) * 1000

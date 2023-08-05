==================
ZTFY.utils package
==================

Introduction
------------

This package is composed of a set of utility functions, which in complement with zope.app.zapi
package can make Zope management easier.


Unicode functions
-----------------

While working with extended characters sets containing accentuated characters, it's necessary to
conversing strings to UTF8 so that they can be used without any conversion problem.

    >>> from ztfy.utils import unicode

'translateString' is a utility function which can be used, for example, to generate an object's id
without space and with accentuated characters converted to their unaccentuated version:

    >>> sample = 'Mon titre accentué'
    >>> unicode.translateString(sample)
    u'mon titre accentue'

Results are lower-cased by default ; this can be avoided be setting the 'forceLower' parameter
to False:

    >>> unicode.translateString(sample, forceLower=False)
    u'Mon titre accentue'

If input string can contain 'slashes' (/) or 'backslashes' (\), they are normally removed ; 
by using the 'escapeSlashes' parameter, the input string is splitted and only the last element is
returned ; this is handy to handle filenames on Windows platform:

    >>> sample = 'Autre / chaîne / accentuée'
    >>> unicode.translateString(sample)
    u'autre chaine accentuee'
    >>> unicode.translateString(sample, escapeSlashes=True)
    u'accentuee'
    >>> sample = 'C:\\Program Files\\My Application\\test.txt'
    >>> unicode.translateString(sample)
    u'cprogram filesmy applicationtest.txt'
    >>> unicode.translateString(sample, escapeSlashes=True)
    u'test.txt'

To remove remaining spaces or convert them to another character, you can use the "spaces" parameter
which can contain any string to be used instead of initial spaces:

    >>> sample = 'C:\\Program Files\\My Application\\test.txt'
    >>> unicode.translateString(sample, spaces=' ')
    u'cprogram filesmy applicationtest.txt'
    >>> unicode.translateString(sample, spaces='-')
    u'cprogram-filesmy-applicationtest.txt'

Spaces replacement is made in the last step, so using it with "escapeSlashes" parameter only affects
the final result:

    >>> unicode.translateString(sample, escapeSlashes=True, spaces='-')
    u'test.txt'


Dates functions
---------------

Dates functions are used to convert dates from/to string representation:

    >>> from datetime import datetime
    >>> from ztfy.utils import date
    >>> now = datetime.fromtimestamp(1205000000)
    >>> now
    datetime.datetime(2008, 3, 8, 19, 13, 20)

You can get an unicode representation of a date in ASCII format using 'unidate' fonction ; date is
converted to GMT:

    >>> udate = date.unidate(now)
    >>> udate
    u'2008-03-08T19:13:20+00:00'

'parsedate' can be used to convert ASCII format into datetime:

    >>> ddate = date.parsedate(udate)
    >>> ddate
    datetime.datetime(2008, 3, 8, 19, 13, 20, tzinfo=<StaticTzInfo 'GMT'>)

'datetodatetime' can be used to convert a 'date' type to a 'datetime' value ; if a 'datetime' value
is used as argument, it is returned 'as is':

    >>> ddate.date()
    datetime.date(2008, 3, 8)
    >>> date.datetodatetime(ddate)
    datetime.datetime(2008, 3, 8, 19, 13, 20, tzinfo=<StaticTzInfo 'GMT'>)
    >>> date.datetodatetime(ddate.date())
    datetime.datetime(2008, 3, 8, 0, 0)


Timezones handling
------------------

Timezones handling game me headaches at first. I finally concluded that the best way (for me !) to handle
TZ data was to store every datetime value in GMT timezone.
As far as I know, there is no easy way to know the user's timezone from his request settings. So you can:
- store this timezone in user's profile,
- define a static server's timezone
- create and register a ServerTimezoneUtility to handle server default timezone.

My current default user's timezone is set to 'Europe/Paris' ; you should probably update this setting in
'timezone.py' if you are located elsewhere.

    >>> from ztfy.utils import timezone
    >>> timezone.tztime(ddate)
    datetime.datetime(2008, 3, 8, 19, 13, 20, tzinfo=<StaticTzInfo 'GMT'>)

'gmtime' function can be used to convert a datetime to GMT:

    >>> timezone.gmtime(now)
    datetime.datetime(2008, 3, 8, 19, 13, 20, tzinfo=<StaticTzInfo 'GMT'>)

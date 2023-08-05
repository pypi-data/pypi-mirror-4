"""easytime - The simplest python time library ever written."""


from datetime import datetime
from pytz import timezone


class easytime(datetime):
    """A simple datetime wrapper."""

    def convert(self, tz='UTC'):
        """Convert this datetime to the specified timezone.

        Usage::

            >>> from easytime import easytime
            >>> current_time_utc = easytime.utcnow()
            >>> current_time_utc
            easytime(2012, 11, 19, 0, 48, 59, 741991)
            >>> current_time_utc.convert('America/Los_Angeles')
            datetime.datetime(2012, 11, 18, 16, 48, 59, 741991, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)
            >>> current_time_utc.convert('Europe/Berlin')
            datetime.datetime(2012, 11, 19, 1, 48, 59, 741991, tzinfo=<DstTzInfo 'Europe/Berlin' CET+1:00:00 STD>)

        :param str tz: The timezone to output the current time in. Defaults to
            'UTC'. You can find a full list of available timezones at:
            http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        :rtype: datetime
        :returns: A python datetime object, with the correct current local time
            of the given timezone.
        """
        current_tz = timezone(self.tzname() or 'UTC')
        return current_tz.localize(self).astimezone(timezone(tz))


# Prevent users from generating naive localtime objects--forces the user to
# *always* use UTC.
easytime.now = easytime.utcnow

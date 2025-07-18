from formulaic.core import Field
from formulaic.coerce import Unicode, BigEndDate, Boolean, UTCDateTime, Integer


class BasicUnicode(Field):
    coerce = [Unicode]


class BasicBoolean(Field):
    coerce = [Boolean]


class DateField(Field):
    coerce = [BigEndDate]


class UTCDateTimeField(Field):
    coerce = [UTCDateTime]


class IntegerField(Field):
    coerce = [Integer]
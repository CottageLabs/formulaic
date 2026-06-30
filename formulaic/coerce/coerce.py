from datetime import date, datetime
import locale

from formulaic.core import Coerce, CoerceError, ErrorCode
from formulaic.lib import dates


class Unicode(Coerce):
    def __init__(self, trim_whitespace=False):
        self.trim_whitespace = trim_whitespace

    def _normalise(self, s):
        if self.trim_whitespace:
            return s.strip()
        return s

    def coerce(self, val, field):
        if val is None:
            return None

        if isinstance(val, str):
            return self._normalise(val)
        elif isinstance(val, bytes):
            try:
                return self._normalise(val.decode("utf8", "strict"))
            except UnicodeDecodeError as e:
                return CoerceError(field, val, UnicodeCoerceDecodeFailCode(self), exception=e)
        else:
            return self._normalise(str(val))

class UnicodeCoerceDecodeFailCode(ErrorCode): id="unicode_coerce_decode_fail"


class Boolean(Coerce):
    def coerce(self, val, field):
        """Conservative boolean cast - don't cast lists and objects to True, just existing booleans and strings."""
        if val is None:
            return None
        if val is True or val is False:
            return val

        if isinstance(val, str):
            if val.lower() == 'true':
                return True
            elif val.lower() == 'false':
                return False
            raise ValueError(
                "Could not convert string {val} to boolean. Expecting string to either say 'true' or 'false' (not case-sensitive).".format(
                    val=val))

        if isinstance(val, int):
            if val == 1:
                return True
            elif val == 0:
                return False
            raise ValueError("Could not convert integer {val} to boolean. Expecting 1 or 0.".format(val=val))

        raise ValueError("Could not convert {val} to boolean. Expect either boolean or string.".format(val=val))


class BigEndDate(Coerce):
    OUT_FORMAT = "%Y-%m-%d"

    def coerce(self, val, field):
        if val is None or val == "":
            return None
        if isinstance(val, date) or isinstance(val, datetime):
            return dates.format(val, format=self.OUT_FORMAT)
        else:
            return dates.reformat(val, out_format=self.OUT_FORMAT)


class Integer(Coerce):
    def coerce(self, val, field):
        # strip any characters that are outside the ascii range - they won't make up the int anyway
        # and this will get rid of things like strange currency marks
        if isinstance(val, str):
            val = val.encode("ascii", errors="ignore")

        # try the straight cast
        try:
            return int(val)
        except ValueError:
            pass

        # could have commas in it, so try stripping them
        try:
            return int(val.replace(",", ""))
        except ValueError:
            pass

        # try the locale-specific approach
        try:
            return locale.atoi(val)
        except ValueError:
            pass

        raise ValueError("Could not convert string to int: {x}".format(x=val))


class LowerCase(Coerce):
    def coerce(self, val, field):
        val = super().coerce(val, field)
        return val.lower()

class UpperCaseUnicode(Unicode):
    def coerce(self, val, field):
        val = super().coerce(val, field)
        return val.upper()

class UTCDateTime(Coerce):
    OUT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def coerce(self, val, field):
        if val is None or val == "":
            return None
        if isinstance(val, date) or isinstance(val, datetime):
            return dates.format(val, format=self.OUT_FORMAT)
        else:
            return dates.reformat(val, out_format=self.OUT_FORMAT)
# -*- coding: utf-8 -*-

# Code written by Dr. Diego Gnesi Bartolani, Archaeologist (diego.gnesi@gmail.com).
# http://www.diegognesi.it

import copy, re
from datetime import datetime, timedelta

class CalendarBase:

    @classmethod
    def get_LPDateTime_from_instance(cls, instance):
        if hasattr(instance, "positive") and hasattr(instance, "second") and hasattr(instance, "microsecond"):
            return instance
        else:
            to_lpd = getattr(instance, "to_LPDateTime", None)
            if callable(to_lpd):
                return to_lpd()
            else:
                return None

    @classmethod
    def from_datetime(cls, datetime_obj):
        dt_instance = CalendarBase.get_LPDateTime_from_instance(datetime_obj)
        return cls.from_LPDateTime(dt_instance)

    @classmethod
    def from_python_datetime(cls, datetime_obj):
        from datando.gregorian import GregorianDateTime
        greg_date = GregorianDateTime(datetime_obj.year, datetime_obj.month, datetime_obj.day, datetime_obj.hour, datetime_obj.minute, datetime_obj.second, datetime_obj.microsecond)
        return cls.from_LPDateTime(cls.get_LPDateTime_from_instance(greg_date))

    @classmethod
    def from_python_timedelta(cls, timedelta_obj):
        seconds = int((timedelta_obj.days * 86400) + timedelta_obj.seconds)
        microseconds = int(timedelta_obj.microseconds)
        seconds += microseconds / 1000000
        microseconds = microseconds % 1000000
        lpd = LPDateTime(True, seconds, microseconds)
        return cls.from_LPDateTime(lpd)

    @classmethod
    def now(cls):
        from datando.gregorian import GregorianDateTime
        n = datetime.now()
        return cls.from_python_datetime(n)

    def __eq__(self, other):
        s = CalendarBase.get_LPDateTime_from_instance(self)
        o = CalendarBase.get_LPDateTime_from_instance(other)
        if s is None or o is None:
            return False
        else:
            return s.positive == o.positive and s.second == o.second and s.microsecond == o.microsecond

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        s = CalendarBase.get_LPDateTime_from_instance(self)
        o = CalendarBase.get_LPDateTime_from_instance(other)
        if s == None or o == None:
            return NotImplemented
        if (s.positive and not o.positive):
            return True
        elif s.positive:
            if s.second > o.second or \
                (s.second == o.second and s.microsecond > o.microsecond):
                return True
            else:
                return False
        else:
            return False

    def __ge__(self, other):
        return self == other or self > other

    def __lt__(self, other):
        return not self >= other

    def __le__(self, other):
        return not self > other

    def __add__(self, other):
        s = CalendarBase.get_LPDateTime_from_instance(self)
        o = CalendarBase.get_LPDateTime_from_instance(other)
        if s == None or o == None:
            return NotImplemented
        if s.positive == o.positive:
            positive = s.positive
            ms = s.microsecond + o.microsecond
            secs = s.second + o.second
            if ms > 1000000:
                 ms -= 1000000
                 secs += 1
        else:
            if s.positive and not o.positive:
                 op1 = s
                 op2 = o
            else:
                 op1 = o
                 op2 = s
            ms = op1.microsecond - op2.microsecond
            secs = op1.second - op2.second
            if ms < 0:
                ms = 1000000 + ms
                secs -= 1
            if secs >= 0:
                positive = True
            else:
                positive = False
                secs = -secs
        return LPDateTime(positive, secs, ms)

    def __sub__(self, other):
        o = CalendarBase.get_LPDateTime_from_instance(other)
        inverse = LPDateTime(not o.positive, o.second, o.microsecond)
        return self + inverse

    def __mul__(self, other):
        x = float(self)
        y = float(other)
        z = x * y
        return LPDateTime.from_float(z)

    def __div__(self, other):
        x = float(self)
        y = float(other)
        z = x / y
        return LPDateTime.from_float(z)

    def __float__(self):
        o = CalendarBase.get_LPDateTime_from_instance(self)
        float_repr = o.second + o.microsecond * 1e-06
        if not o.positive:
            float_repr = float_repr * -1
        return float_repr

class LPDateTime(CalendarBase):
    def __init__(self, positive = True, second = 0, microsecond = 0):
        self.positive = positive
        self.second = second
        self.microsecond = microsecond

    def __str__(self):
        if self.positive:
            sign = "+"
        else:
            sign = "-"
        return "{0}{1}.{2:06d}".format(sign, self.second, self.microsecond)

    @classmethod
    def parse(cls, date_string):
        reg_expr = r'^(?P<sign>\+|\-){0,1}(?P<ss>\d+).(?P<ms>\d{1, 6})$'
        m = re.match(reg_expr, date_string)
        if m:
            gd = m.groupdict()
            second = int(gd['ss'])
            microsecond = int(gd['ms'])
            positive == (not (gd['sign'] == '-'))
            return LPInterval(positive, second, microsecond)
        else:
            return None

    @staticmethod
    def get_prefix():
        return ""

    @classmethod
    def from_float(cls, number):
        second = int(number)
        microsecond = int((number - second) * 1e+06)
        positive = (number >= 0)
        return LPDateTime(positive, abs(second), microsecond)

    @classmethod
    def from_LPDateTime(cls, dt):
        return LPDateTime(dt.positive, dt.second, dt.microsecond)

    @classmethod
    def from_timespan(cls, days = 0, hours = 0, minutes = 0, seconds = 0, microseconds = 0):
        if days >= 0:
            abs_days = days
            positive = True
        else:
            abs_days = -days
            positive = False
        secs = abs_days * 86400 + hours * 3600 + minutes * 60 + seconds
        return LPDateTime(positive, secs, microseconds)

    def to_timespan_string(self):
        days = self.second / 86400
        lt_day = self.second % 86400
        hours = lt_day / 3600
        lt_hour = lt_day % 3600
        minutes = lt_hour / 60
        seconds = lt_hour % 60
        if self.positive:
            sign = "+"
        else:
            sign = "-"
        return "{0}{1} days, {2} hours, {3} minutes, {4} seconds, {5} microseconds".format(sign, days, hours, minutes, seconds, self.microsecond)

class LPInterval:
    def __init__(self, start, end, fuzzy_start = None, fuzzy_end = None, fuzzy_function = None):
        # Valid values for fuzzy_membership_function are "trapezoidal", "logistic" and "gaussian"
        self.start = start
        self.end = end
        if fuzzy_start == None:
            self.fuzzy_start = self.start
        else:
            self.fuzzy_start = fuzzy_start
        if fuzzy_end == None:
            self.fuzzy_end = self.end
        else:
            self.fuzzy_end = fuzzy_end
        if fuzzy_function == None:
            self.fuzzy_function = 'trapezoidal'
        else:
            self.fuzzy_function = fuzzy_function

    @classmethod
    def from_month(cls, year, month, datetime_class):
        fm = getattr(datetime_class, "get_interval_by_month", None)
        if fm == None:
            return None
        else:
            return fm(year, month)

    @classmethod
    def from_year(cls, year, datetime_class):
        fm = getattr(datetime_class, "get_interval_by_year", None)
        if fm == None:
            return None
        else:
            return fm(year)
    @classmethod
    def from_century(cls, century, datetime_class):
        fm = getattr(datetime_class, "get_interval_by_century", None)
        if fm == None:
            return None
        else:
            return fm(century)

    @classmethod
    def from_millennium(cls, millennium, datetime_class):
        fm = getattr(datetime_class, "get_interval_by_millennium", None)
        if fm == None:
            return None
        else:
            return fm(millennium)

    def __str__(self):
        f_string = "Interval \ START {0} ; END {1} ; FUZZY START {2} ; FUZZY END {3} ; FUZZY FUNCTION {4}"
        return f_string.format(self.start, self.end, self.fuzzy_start, self.fuzzy_end, self.fuzzy_function)

    @classmethod
    def parse(cls, date_string):
        from datando import parser
        reg_expr = r'^Interval \\ START (?P<start>.+) ; END (?P<end>.+) ; FUZZY START (?P<fuzzystart>.+) ; FUZZY END (?P<fuzzyend>.+) ; FUZZY FUNCTION (?P<fuzzyfun>.+)$'
        m = re.match(reg_expr, date_string)
        if m:
            gd = m.groupdict()
            str_start = gd['start']
            str_end = gd['end']
            str_fuzzystart = gd['fuzzystart']
            str_fuzzyend = gd['fuzzyend']
            fuzzyfun = gd['fuzzyfun']
            start = parser.parse(str_start)
            end = parser.parse(str_end)
            fuzzystart = parser.parse(str_fuzzystart)
            fuzzyend = parser.parse(str_fuzzyend)
            if start and end and fuzzystart and fuzzyend:
                return LPInterval(start, end, fuzzystart, fuzzyend, fuzzyfun)
        # Unable to parse a period or a specific date.
        return None

    @staticmethod
    def get_prefix():
        return "Interval \\"

    def contains(self, date_or_interval):
        return self.start <= date_or_interval and self.end >= date_or_interval

    def narrowly_contains(self, date_or_interval):
        return self.start < date_or_interval and self.end > date_or_interval

    def overlaps(self, lp_interval):
        return self.start <= lp_interval.end and self.end >= lp_interval.start

    def narrowly_overlaps(self, lp_interval):
        return self.start < lp_interval.end and self.end > lp_interval.start

    def union(self, other_interval):
        # Fuzzy memeberhip function is taken from the caller instance (or from other_interval,
        # if in the caller object this attribute is None).
        if self.overlaps(other_interval):
            if self.start <= other_interval.start:
                new_start = self.start
            else:
                new_start = other_interval.start
            if self.end >= other_interval.end:
                new_end = self.end
            else:
                new_end = other_interval.end
            if self.fuzzy_start != None and other_interval.fuzzy_start != None:
                if self.fuzzy_start <= other_interval.fuzzy_start:
                    new_fuzzy_start = self.fuzzy_start
                else:
                    new_fuzzy_start = other_interval.fuzzy_start
            elif self.fuzzy_start != None:
                new_fuzzy_start = self.fuzzy_start
            elif other_interval.fuzzy_start != None:
                new_fuzzy_start = other_interval.fuzzy_start
            else:
                new_fuzzy_start = None
            if self.fuzzy_end != None and other_interval.fuzzy_end != None:
                if self.fuzzy_end >= other_interval.fuzzy_end:
                    new_fuzzy_end = self.fuzzy_end
                else:
                    new_fuzzy_end = other_interval.fuzzy_end
            elif self.fuzzy_end != None:
                new_fuzzy_end = self.fuzzy_end
            elif other_interval.fuzzy_end != None:
                new_fuzzy_end = other_interval.fuzzy_end
            else:
                new_fuzzy_end = None
            if self.fuzzy_function == None and other_interval.fuzzy_function == None:
                new_fuzzy_function = None
            elif self.fuzzy_function == None:
                new_fuzzy_function = other_interval.fuzzy_function
            else:
                new_fuzzy_function = self.fuzzy_function
            new_interval = LPInterval(new_start, new_end, new_fuzzy_start, new_fuzzy_end, new_fuzzy_function)
            return copy.deepcopy(new_interval)
        else:
            return None

    def intersection(self, other_interval):
        # Fuzzy memeberhip function is taken from the caller instance (or from other_interval,
        # if in the caller object this attribute is None).
        if self.overlaps(other_interval):
            if self.start <= other_interval.start:
                new_start = other_interval.start
            else:
                new_start = self.start
            if self.end >= other_interval.end:
                new_end = other_interval.end
            else:
                new_end = self.end
            if self.fuzzy_start != None and other_interval.fuzzy_start != None:
                if self.fuzzy_start <= other_interval.fuzzy_start:
                    new_fuzzy_start = other_interval.fuzzy_start
                else:
                    new_fuzzy_start = self.fuzzy_start
            elif self.fuzzy_start != None:
                new_fuzzy_start = self.fuzzy_start
            elif other_interval.fuzzy_start != None:
                new_fuzzy_start = other_interval.fuzzy_start
            else:
                new_fuzzy_start = None
            if self.fuzzy_end != None and other_interval.fuzzy_end != None:
                if self.fuzzy_end >= other_interval.fuzzy_end:
                    new_fuzzy_end = other_interval.fuzzy_end
                else:
                    new_fuzzy_end = self.fuzzy_end
            elif self.fuzzy_end != None:
                new_fuzzy_end = self.fuzzy_end
            elif other_interval.fuzzy_end != None:
                new_fuzzy_end = other_interval.fuzzy_end
            else:
                new_fuzzy_end = None
            if self.fuzzy_function == None and other_interval.fuzzy_function == None:
                new_fuzzy_function = None
            elif self.fuzzy_function == None:
                new_fuzzy_function = other_interval.fuzzy_function
            else:
                new_fuzzy_function = self.fuzzy_function
            new_interval = LPInterval(new_start, new_end, new_fuzzy_start, new_fuzzy_end, new_fuzzy_function)
            return copy.deepcopy(new_interval)
        else:
            return None
        pass

    def __eq__(self, other):
        if hasattr(other, "start") and hasattr(other, "end"):
            return self.start == other.start and self.end == other.end
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if hasattr(other, "start") and hasattr(other, "end"):
            return self.start < other.start or (self.start == other.start and self.end < other.end)
        else:
            return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        le_result = self <= other
        if le_result == NotImplemented:
            return le_result
        else:
            return not le_result

    def __ge__(self, other):
        return self == other or self > other

    def duration(self):
        return self.end - self.start

    def fuzzy_membership(self, lp_datetime):
        if self.contains(lp_datetime):
            return 1.0
        elif not (self.fuzzy_start is None or self.fuzzy_function is None) and lp_datetime >= self.fuzzy_start and lp_datetime <= self.start:
            if self.fuzzy_function == "trapezoidal":
                # Nota: Manca del codice qui!!!
                f_start = float(self.start)
                f_fuzzy_start = float(self.fuzzy_start)
                f_diff = f_start - f_fuzzy_start
                f_dt = float(lp_datetime)
                dt_position = f_dt - f_fuzzy_start
                return dt_position / f_diff
        elif not (self.fuzzy_end is None or self.fuzzy_function is None) and lp_datetime <= self.fuzzy_end and lp_datetime >= self.end:
            if self.fuzzy_function == "trapezoidal":
                # Nota: Manca del codice qui!!!
                f_end = float(self.end)
                f_fuzzy_end = float(self.fuzzy_end)
                f_diff = f_fuzzy_end - f_end
                f_dt = float(lp_datetime)
                dt_position = f_dt - f_end
                return dt_position / f_diff
            else:
                raise NotImplementedError()
        else:
            return 0

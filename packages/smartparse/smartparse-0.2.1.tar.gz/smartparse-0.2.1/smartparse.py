import ConfigParser
import datetime
import timeparser


timeparser.TimeFormats.config(
    seps=[':'],
    allow_no_sep=False,
    figures=[False, True, True],
    )
#TODO: let it default to little-endian;
timeparser.DateFormats.config(
    endian=timeparser.BIG_ENDIAN,
    seps=['.', '/', '-'],
    allow_no_sep=False,
    figures=[False, True, True],
    )
timeparser.DatetimeFormats.config(
    seps=[' ', '_'],
    allow_no_sep=False,
    )

def time_config(*args, **kwargs):
    """
    Calls timeparser.TimeFormats.config.

    Kwargs:
        seps (list):        separators formats are generated with
        figures (list):     list of three boolean that predicts how many
                            digits the formats have.
        allow_no_sep (bool):    allows formats without separators ('%d%m%y')
        microsec (bool):    if True also formats with '%f' for microseconds
                            are produced.
    """
    timeparser.TimeFormats.config(*args, **kwargs)

def date_config(*args, **kwargs):
    """
    Calls timeparser.DateFormats.config.

    Kwargs:
        seps (list):        separators formats are generated with
        figures (list):     list of three boolean that predicts how many
                            digits the formats have.
        allow_no_sep (bool):    allows formats without separators ('%d%m%y')
        allow_month_name (bool):    if True also '%b' and '%B' are used to
                                    produce formats.
        endian (int):               determines the order for dates (s.a.)

    Endianness is the order in which day, month and year constitutes a date.
    This module defines three constants:
    LITTLE_ENDIAN (little first):   day, month, year
    BIG_ENDIAN (biggest first):     year, month, day
    MIDDLE_ENDIAN (middle first):   month, day, year
    Use one of these constants as value for the endian-parameter.
    """
    timeparser.DateFormats.config(*args, **kwargs)

def datetime_config(*args, **kwargs):
    """
    Calls timeparser.DatetimeFormats.config.

    Kwargs:
        seps (list):        separators formats are generated with
        allow_no_sep (bool):    allows formats without separators ('%d%m%y')
    """
    timeparser.DatetimeFormats.config(*args, **kwargs)


class SmartParserMixin:
    """Extension for SafeConfigParser
    
    Adds some useful methods: getlist, gettime, xget and xitems
    """
    def _checklen(self, list):
        """Raises ValueError if len(list) is smaller than two.
        
        Used in xget, to prevent every value to be converted into a list.
        """
        if len(list) < 2: raise ValueError('list is too short')
        else: return list

    def gettime(self, section, option):
        """Get option as datetime.time-instance.

        Expects a ':' as separator. If converting failes raises ValueError.
        Minutes or seconds are dispensable.
        """
        return timeparser.parsetime(self.get(section, option))

    def getdate(self, section, option):
        """Get option as datetime.date-instance.

        Format needs to be 'YEAR.MONTH.DAY'.
        If converting failes raises ValueError.
        """
        return timeparser.parsedate(self.get(section, option))

    def getdatetime(self, section, option):
        """Get option as datetime.datetime-instance.

        Expected format is 'YEAR.MONTH.DAY HOUR[:MINUTE[:SECOND]]'.
        If converting failes raises ValueError.
        """
        return timeparser.parsedatetime(self.get(section, option))

    def getlist(self, section, option):
        """Get option as list.
        """
        return self.get(section, option).split()

    def getsmartlist(self, section, option):
        """Get option as list. Also tries to convert the list-items.
        
        List-items are converted either into an int, float
        or a datetime.time-intance.
        """
        list = self.getlist(section, option)
        for i in range(0, len(list)):
            try: list[i] = int(list[i])
            except ValueError: pass
            else: continue
            try: list[i] = float(list[i])
            except ValueError: pass
            else: continue
            try: list[i] = timeparser.parsetime(list[i])
            except ValueError: pass
            else: continue
            try: list[i] = timeparser.parsedate(list[i])
            except ValueError: pass
            else: continue
            try: list[i] = timeparser.parsedatetime(list[i])
            except ValueError: pass
            else: continue
        return list

    def xget(self, section, option):
        """Get option either as int, float, boolean, datetime.time-instance, as
        smartlist or simply as string.
        """
        try: return self.getint(section, option)
        except Exception: pass
        try: return self.getfloat(section, option)
        except Exception: pass
        try: return self.getboolean(section, option)
        except Exception: pass
        try: return self.gettime(section, option)
        except Exception: pass
        try: return self.getdate(section, option)
        except Exception: pass
        try: return self.getdatetime(section, option)
        except Exception: pass
        try: return self._checklen(self.getsmartlist(section, option))
        except Exception: pass
        return self.get(section, option)

    def xitems(self, section):
        """Get items of section using xget to recieve all options.
        """
        options = self.options(section)
        items = list()
        for opt in options:
            items.append((opt, self.xget(section, opt)))
        return items


class RawSmartParser(SmartParserMixin, ConfigParser.RawConfigParser):
    """
    SmartParser based on the ConfigParser.RawConfigParser.

    Provides methods to parse options as objects of the datetime-modules, as
    list or as 'smartlist'.

    Items of a smartlist are automatically tried to converted into different
    types (such as: int, float, time, date, datetime).

    It also provides additional get- and itme-methods (xget, xitem):
    xget tries to get the option as one of the following types (in this
    order): int, float, boolean, time, date, datetime, smartlist.
    If every type fails the option is given as string.
    """


class SmartParser(SmartParserMixin, ConfigParser.ConfigParser):
    """
    SmartParser based on the ConfigParser.ConfigParser.
    """


class SafeSmartParser(SmartParserMixin, ConfigParser.SafeConfigParser):
    """
    SmartParser based on the ConfigParser.SafeConfigParser.
    """





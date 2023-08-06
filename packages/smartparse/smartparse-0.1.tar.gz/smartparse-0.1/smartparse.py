import ConfigParser
import datetime
from datetimeparser import DateTimeParser



class SmartParserMixin(DateTimeParser):
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
        return self.parsetime(self.get(section, option))

    def getdate(self, section, option):
        """Get option as datetime.date-instance.

        Format needs to be 'YEAR.MONTH.DAY'.
        If converting failes raises ValueError.
        """
        return self.parsedate(self.get(section, option))

    def getdatetime(self, section, option):
        """Get option as datetime.datetime-instance.

        Expected format is 'YEAR.MONTH.DAY HOUR[:MINUTE[:SECOND]]'.
        If converting failes raises ValueError.
        """
        return self.parsedatetime(self.get(section, option))

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
            try: list[i] = self.parsetime(list[i])
            except ValueError: pass
            else: continue
            try: list[i] = self.parsedate(list[i])
            except ValueError: pass
            else: continue
            try: list[i] = self.parsedatetime(list[i])
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





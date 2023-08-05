import calendar
import datetime
import logging
import re
import textwrap
import time
from activitytracker.base import MONTHS, MONTH_NAMES, find_config_file

logger = logging.getLogger('activitytracker')

ONE_DAY = datetime.timedelta(days=1)

WEEKDAY_NAMES = [u'monday', u'tuesday', u'wednesday',
                 u'thursday', u'friday', u'saturday', u'sunday']
WEEKDAYS = {}
for x, weekday in enumerate(WEEKDAY_NAMES):
    WEEKDAYS[weekday] = x
    WEEKDAYS[x] = weekday
    WEEKDAYS[weekday[:3]] = x
    WEEKDAYS[weekday[:2]] = x

FORMATTERS = {}


def out(s='', padding=''):
    s = textwrap.fill(s, initial_indent=padding,
                      subsequent_indent=padding + '  ')
    print s


def pretty(v):
    for types, func in FORMATTERS.items():
        if isinstance(v, types):
            return func(v)

    return str(v)


def _pretty_timedelta(v):
    """Create a formatted string for the given timedelta object.

      >>> from datetime import timedelta

      >>> _pretty_timedelta(timedelta(hours=3))
      u'3.0 hrs'

      >>> _pretty_timedelta(timedelta(minutes=45))
      u'45 mins'

      >>> _pretty_timedelta(timedelta(hours=2, minutes=54))
      u'2.9 hrs'
    """

    hours = (v.days * 24.0) + (v.seconds / 3600.0)
    if hours >= 1.0:
        return u'%s hrs' % hours
    else:
        return u'%.0f mins' % (hours * 60.0)

FORMATTERS[(datetime.timedelta,)] = _pretty_timedelta


def _pretty_datetime(v):
    """Create a formatted string for the given timedelta object.

      >>> from datetime import datetime, date, time

      >>> _pretty_datetime(datetime(2007, 5, 7, 3, 30))
      u'Mon, May 7, 2007 3:30am'

      >>> _pretty_datetime(date(2007, 03, 22))
      u'Thu, Mar 22, 2007'

      >>> _pretty_datetime(time(13, 21))
      u'1:21pm'
    """

    tm = None
    date = None

    if isinstance(v, (datetime.date, datetime.datetime)):
        date = MONTHS[v.month][:3].title()
        date += u' ' + unicode(v.day) + u', ' + unicode(v.year)
        date = WEEKDAYS[calendar.weekday(v.year, v.month, v.day)] \
               [:3].title() + ', ' + date

    if isinstance(v, (datetime.time, datetime.datetime)):
        ampm = u'am'
        hour = v.hour
        if hour >= 12:
            ampm = u'pm'
        if hour > 12:
            hour = hour - 12
        if hour == 0:
            hour = 12
            ampm = u'am'

        smin = unicode(v.minute)
        if len(smin) == 1:
            smin = u'0' + smin
        tm = unicode(hour) + u':' + smin + ampm

    if date and tm:
        return date + u' ' + tm
    elif date:
        return date
    elif tm:
        return tm
FORMATTERS[(datetime.datetime, datetime.date, datetime.time)] = \
                               _pretty_datetime

XML_ESCAPE_CODES = {'&gt;': '>',
                    '&lt;': '<'}


def last_monthday(dt):
    """Retrive the date representing the last day of the month.

      >>> from datetime import datetime, date

      >>> last_monthday(datetime(2003, 03, 27))
      datetime.date(2003, 3, 31)

      >>> last_monthday(date(2003, 11, 23))
      datetime.date(2003, 11, 30)

      >>> last_monthday(date(2003, 2, 2))
      datetime.date(2003, 2, 28)

      >>> last_monthday(date(2000, 2, 2))
      datetime.date(2000, 2, 29)
    """

    t = datetime.datetime(dt.year, dt.month, dt.day)
    while t.month == dt.month:
        t += ONE_DAY
    t -= ONE_DAY

    return t.date()


class ProjectContainer(object):
    """A collection of project objects.  An importtant implementation note
    is that this container will automatically create projects when a project
    is trying to be retrieved via the [] interface.  So an error being raised
    or None being returned will never happen.  Also note that even though
    a project container thinks it has intervals, it's interval list will
    be empty (an empty tuple).

      >>> container = ProjectContainer()
      >>> container['abc/def'].intervals
      []

      >>> container['abc/ghi'].intervals
      []

      >>> len(container)
      1

      >>> len(container['abc'])
      2
    """

    intervals = ()
    formatted_name = None

    def __init__(self):
        self._data = {}
        self._name_map = {}

    def keys(self):
        return self._data.keys()

    def fullkeys(self):
        keys = []
        for x in self.projects:
            keys += x.fullkeys()
        return keys

    def __getitem__(self, k):
        k = unicode(k or '').lower()

        prj = self
        items = [x.strip() for x in k.split('/', 1)]
        prj = self._localgetitem(items[0])

        if len(items) > 1:
            return prj[items[1]]

        return prj

    def _localgetitem(self, k):
        prj = self._data.get(k, None)
        if prj is None:
            prj = Project(k)
            self._data[k] = prj
        return prj

    def __delitem__(self, k):
        k = k or ''

        prj = self
        items = k.split('/', 1)
        if len(items) == 1:
            del self._data[items[0]]
        else:
            prj = self._data[items[0]]
            del prj['/'.join(items[1:])]

    def items(self):
        return self._data.items()

    @property
    def projects(self):
        return self._data.values()

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return self._single_str()

    def _single_str(self, padding_count=0):
        padding = ' ' * padding_count
        if self.formatted_name:
            s = padding + self.formatted_name + '\n'
        else:
            s = ''

        for key, value in self._data.items():
            s += padding + value._single_str(padding_count + 1)
        return s

    def copy(self, deep=False):
        newcontainer = ProjectContainer()
        if deep:
            for key, value in self._data.items():
                newcontainer._data[key] = value.copy(deep)
        return newcontainer

    @property
    def interval_time(self):
        total = datetime.timedelta()
        for x in self.intervals:
            total += x.total
        return total

    @property
    def total_interval_time(self):
        total = datetime.timedelta()
        for x in self.intervals:
            total += x.total
        for x in self.projects:
            total += x.total_interval_time
        return total

    def has_intervals(self, deepcheck=False):
        if deepcheck:
            for prj in self.projects:
                if prj.has_intervals(True):
                    return True

        return len(self.intervals) > 0

    @property
    def earliest_interval(self):
        earliest = None
        interval = None
        for x in self.intervals:
            if earliest is None or x.start < earliest:
                earliest = x.start
                interval = x
        for x in self.projects:
            checkinterval = x.earliest_interval
            if earliest is None or checkinterval.start < earliest:
                earliest = checkinterval.start
                interval = checkinterval

        return interval

    @property
    def latest_interval(self):
        latest = None
        interval = None
        for x in self.intervals:
            if latest is None or x.start > latest:
                interval = x
        for x in self.projects:
            checkinterval = x.latest_interval
            if latest is None or checkinterval.start > latest:
                latest = checkinterval.start
                interval = checkinterval

        return interval


class Project(ProjectContainer):
    """Basically a project container with a name and possible intervals.

      >>> project = Project('foo')
      >>> project.formatted_name
      u'foo'
    """

    intervals = None
    name = None

    def __init__(self, name):
        super(Project, self).__init__()
        self.name = name
        self.intervals = []

    def fullkeys(self):
        keys = []
        keys.append(self.name)
        for x in self.projects:
            keys += [self.name + '/' + x for x in x.fullkeys()]
        return keys

    def prjkeys_without_intervals(self):
        keys = set()
        for name, prj in self._data.items():
            for without in prj.prjkeys_without_intervals():
                keys.add(name + '/' + without)
            if not prj.has_intervals(True):
                keys.add(name)
        return keys

    @property
    def formatted_name(self):
        t1 = self.interval_time
        t2 = self.total_interval_time
        if (t1.days > 0 or t1.seconds > 0 or t1.microseconds > 0) and t1 != t2:
            total = u' (%s -- %s)' % (pretty(t1), pretty(t2))
        elif t2.days > 0 or t2.seconds > 0 or t2.microseconds > 0:
            total = u' (%s)' % pretty(t2)
        else:
            total = ''
        return u'%s%s' % (self.name, total)

    def copy(self, deep=False):
        newprj = Project(self.name)
        newprj.intervals = list(self.intervals)

        if deep:
            for key, value in self._data.items():
                newprj._data[key] = value.copy(deep)
        return newprj


parser_factories = {}


def get_parser_factory(name):
    factory = parser_factories.get(name, None)

    if factory is None:
        lastpos = name.rfind('.')
        parsermod = __import__(name[:lastpos], globals(), locals(), [''])
        try:
            factory = getattr(parsermod, name[lastpos + 1:])
        except AttributeError, e:
            raise ValueError('Could not load the factory plugin named %r '
                             '(original message is %r)' % (name, str(e)))
        parser_factories[name] = factory

    return factory


class TimeTracker(object):
    """An instance of this class will maintain state within itself.
    """

    def __init__(self):
        self.projects = ProjectContainer()

    def parse(self, filenames, parser_name):
        """In general activitytracker monitors state while parsing.  But,
        the parse() function will erase state for current time, current date,
        current note, and current project for every file that is parsed.
        """

        logger.info('Using parser: %s' % parser_name)
        parser = get_parser_factory(parser_name)(self.projects,
                                                 self.default_project)

        args = filenames
        filenames = []
        for x in args:
            if isinstance(x, (tuple, list)):
                filenames += list(x)
            else:
                filenames.append(str(x))

        for filename in filenames:
            logger.info("Parsing %r" % filename)
            f = open(filename)
            try:
                parser.parse_input(f)
            finally:
                f.close()

RE_DATE = re.compile('([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])')


def first_weekday(d):
    """Determine the first day of the week.  At this time the first day
    of the week is derived via the standard python calendar module's
    firstweekday() function.

      >>> from datetime import date

      >>> first_weekday(date(2004, 03, 29))
      datetime.date(2004, 3, 29)

      >>> first_weekday(date(2007, 01, 3))
      datetime.date(2007, 1, 1)
    """

    checking = datetime.datetime(d.year, d.month, d.day)
    while calendar.weekday(checking.year,
                           checking.month,
                           checking.day) != calendar.firstweekday():
        checking -= ONE_DAY
    return checking.date()


def estimate_startstop(datestr, nowfactory=None):
    """While handling user defined text it can be good to estimate the
    intended start and stop datetime's.  Requires using YYYY-MM-DD format
    when specifying absolute dates.  The nowfactory argument is meant to be
    some callable that will return the time 'right now'.

      >>> estimate_startstop('2007-05-05')
      (datetime.datetime(2007, 5, 5, 0, 0),
       datetime.datetime(2007, 5, 5, 23, 59))
      >>> estimate_startstop('2007-05-05:2007-07-07')
      (datetime.datetime(2007, 5, 5, 0, 0),
       datetime.datetime(2007, 7, 7, 23, 59))

    Make sure english month name matching works.

      >>> startstop = estimate_startstop('march')
      >>> (startstop[0].month, startstop[1].month)
      (3, 3)

      >>> startstop = estimate_startstop('nov')
      >>> (startstop[0].month, startstop[1].month)
      (11, 11)

    And english week day names.

      >>> from calendar import weekday
      >>> startstop = estimate_startstop('tuesday')
      >>> weekday(startstop[0].year, startstop[0].month, startstop[0].day)
      1

      >>> startstop = estimate_startstop('fri')
      >>> weekday(startstop[0].year, startstop[0].month, startstop[0].day)
      4

      >>> from datetime import datetime
      >>> def nowfactory(): return datetime(2006, 5, 7, 15, 23)

      >>> estimate_startstop('today', nowfactory)
      (datetime.datetime(2006, 5, 7, 0, 0),
       datetime.datetime(2006, 5, 7, 23, 59))

      >>> estimate_startstop('yesterday', nowfactory)
      (datetime.datetime(2006, 5, 6, 0, 0),
       datetime.datetime(2006, 5, 6, 23, 59))

      >>> estimate_startstop('week', nowfactory)
      (datetime.datetime(2006, 5, 1, 0, 0),
       datetime.datetime(2006, 5, 7, 23, 59))

      >>> estimate_startstop('lastweek', nowfactory)
      (datetime.datetime(2006, 4, 24, 0, 0),
       datetime.datetime(2006, 4, 30, 23, 59, 59))

      >>> estimate_startstop('1', nowfactory)
      (datetime.datetime(1, 1, 1, 0, 0),
       datetime.datetime(1, 12, 31, 23, 59))

      >>> estimate_startstop('apr', nowfactory)
      (datetime.datetime(2006, 4, 1, 0, 0),
       datetime.datetime(2006, 4, 30, 23, 59))

      >>> estimate_startstop('2000:2004', nowfactory)
      (datetime.datetime(2000, 1, 1, 0, 0),
       datetime.datetime(2004, 12, 31, 23, 59))

"""

    if not datestr:
        raise ValueError('datestr cannot be empty')

    if nowfactory is None:
        nowfactory = datetime.datetime.now

    def handle_one(onedatestr):

        if onedatestr == 'all':
            start = None
            stop = None
        elif onedatestr == 'today':
            start = nowfactory()
            start = datetime.datetime(start.year, start.month, start.day)
            stop = datetime.datetime(start.year, start.month,
                                     start.day, 23, 59)
        elif onedatestr == 'yesterday':
            start = nowfactory() - ONE_DAY
            start = datetime.datetime(start.year, start.month, start.day)
            stop = datetime.datetime(start.year, start.month,
                                     start.day, 23, 59)
        elif onedatestr == 'lastweek':
            start = nowfactory()
            start = datetime.datetime(start.year, start.month, start.day)
            start = first_weekday(start)
            start = datetime.datetime(start.year, start.month, start.day) \
                    - datetime.timedelta(days=7)
            stop = start + datetime.timedelta(days=6,
                                              minutes=1439, seconds=59)
        elif onedatestr == 'week':
            start = nowfactory()
            start = datetime.datetime(start.year, start.month, start.day)
            stop = datetime.datetime(start.year, start.month,
                                     start.day, 23, 59)
            start = first_weekday(start)
            start = datetime.datetime(start.year, start.month, start.day)
        elif onedatestr == 'month':
            start = nowfactory()
            start = datetime.datetime(start.year, start.month, 1)
            stop = last_monthday(start)
            stop = datetime.datetime(stop.year, stop.month, stop.day, 23, 59)
        elif onedatestr == 'year':
            start = nowfactory()
            start = datetime.datetime(start.year, 1, 1)
            stop = nowfactory()
            stop = datetime.datetime(stop.year, stop.month, stop.day, 23, 59)
        else:
            if RE_DATE.match(onedatestr) is not None:
                start = datetime.datetime(*time.strptime(onedatestr,
                                                         '%Y-%m-%d')[:3])
                stop = datetime.datetime(start.year, start.month,
                                         start.day, 23, 59)
            else:
                vals = onedatestr.split('-')
                if len(vals) == 1 and vals[0].isdigit():
                    year = int(vals[0])
                    start = datetime.datetime(year, 1, 1)
                    days = 364
                    if calendar.isleap(year):
                        days = 365
                    stop = start + datetime.timedelta(days=days,
                                                      minutes=60 * 23 + 59)
                elif len(vals) == 2 and vals[0].isdigit() \
                         and vals[1].isdigit():
                    year = int(vals[0])
                    month = int(vals[1])
                    start = datetime.datetime(year, month, 1)
                    days = 364
                    if calendar.isleap(year):
                        days = 365
                    stop = start + datetime.timedelta(days=days,
                                                      minutes=60 * 23 + 59)
                else:
                    # do some word checks for months
                    start = None
                    for pos, month in enumerate(MONTH_NAMES):
                        if month is not None and month.startswith(onedatestr):
                            month_index = pos
                            start = nowfactory()
                            start = datetime.datetime(start.year,
                                                      month_index, 1)
                            stop = last_monthday(start)
                            stop = datetime.datetime(stop.year, stop.month,
                                                     stop.day, 23, 59)
                            break


                    if start is None:
                        for pos, weekday in enumerate(WEEKDAY_NAMES):
                            if weekday.startswith(onedatestr):
                                start = nowfactory()
                                while calendar.weekday(start.year, start.month,
                                                       start.day) != pos:
                                    start -= ONE_DAY

                                start = datetime.datetime(start.year,
                                                          start.month,
                                                          start.day,
                                                          0, 0)
                                stop = datetime.datetime(start.year,
                                                         start.month,
                                                         start.day,
                                                         23, 59)
                                break

                    if start is None:
                        raise ValueError("Couldn't derive a date value from %r"
                                         % onedatestr)

        return start, stop

    args = datestr.split(':')
    if len(args) > 2:
        raise ValueError('Can only handle two date values')

    start, end = handle_one(args[0])
    if len(args) > 1:
        ignorestart, end = handle_one(args[1])

    return (start, end)


class TrackerReporter(object):
    """A helper class for formatting reports on a given tracker.
    """

    def __init__(self, tracker):
        self.tracker = tracker

    def _remove_invalid(self, container, date_start, date_end,
                        project_filter):

        for prj in container.projects:
            intervals = []
            for x in prj.intervals:
                if x.start >= date_start and x.stop <= date_end:
                    intervals.append(x)
            prj.intervals = intervals
            self._remove_invalid(prj, date_start, date_end, project_filter)

    def filtered_results(self, date_start=None, date_end=None,
                         project_filter=[]):
        container = self.tracker.projects.copy(True)

        self._remove_invalid(container, date_start, date_end, project_filter)
        empty = set()
        for name, prj in container.items():
            for key in prj.prjkeys_without_intervals():
                empty.add(name + '/' + key)

            if not prj.has_intervals(True):
                empty.add(name)

        for key in reversed(sorted(empty)):
            del container[key]

        if project_filter:
            newcontainer = ProjectContainer()
            for key in container.fullkeys():
                for prj in project_filter:
                    if key.find(prj) > -1:
                        newprj = newcontainer[key]
                        newprj.intervals = container[key].intervals
            container = newcontainer

        return container

    def build_by_date(self, datedict, root, container=None, ancestors=[]):
        if container is None:
            container = root

        ancestorkey = '/'.join(ancestors)
        if ancestorkey:
            ancestorkey += '/'

        for prj in container.projects:
            for interval in prj.intervals:
                d = interval.start.date()
                month = datedict.get((d.year, d.month), None)
                if month is None:
                    month = {}
                    datedict[(d.year, d.month)] = month
                existing = month.get(d, None)
                if existing is None:
                    existing = ProjectContainer()
                    month[d] = existing
                existing[ancestorkey + prj.name].intervals.append(interval)
            newancestors = ancestors + [prj.name]
            self.build_by_date(datedict, root, prj, newancestors)

    def print_results(self,
                      date_start=None,
                      date_end=None,
                      display_intervals=False,
                      display_notes=False,
                      project_filter=[]):

        if date_start is not None or date_end is not None or project_filter:
            container = self.filtered_results(date_start, date_end,
                                              project_filter)
        else:
            container = self.tracker.projects

        out()
        out("Filter: %s  ---  %s" % (pretty(date_start), pretty(date_end)))

        earliest = container.earliest_interval
        if earliest is not None:
            earliest = pretty(earliest.start)
        else:
            earliest = 'N/A'
        latest = container.latest_interval
        if latest is not None:
            latest = pretty(latest.start)
        else:
            latest = 'N/A'

        out()
        total = pretty(container.total_interval_time)
        out('Months (%s):' % total)
        d = {}
        self.build_by_date(d, container)
        for smonth in sorted(d.keys()):
            month = d[smonth]
            month_total = datetime.timedelta()
            for c in month.values():
                month_total += c.total_interval_time
            out('%i, %s (%s)' % (smonth[0], MONTHS[smonth[1]].title(),
                                 pretty(month_total)),
                '  ')
            for day in sorted(month.keys()):
                c = month[day]
                out('%s (%s)' % (pretty(day),
                                 pretty(c.total_interval_time)),
                    '    ')
                self.print_container(c, '    ', display_intervals,
                                     display_notes)

        out()
        out('Totals (%s):' % total)
        for prj_name in sorted(container.keys()):
            prj = container[prj_name]
            self.print_container(container=prj, padding='  ')
        out()

    def print_container(self,
                        container,
                        padding='',
                        display_intervals=False,
                        display_notes=False):
        if container.formatted_name:
            out(container.formatted_name, padding)

        if display_intervals:
            for interval in container.intervals:
                out('%s to %s (%s)' % (pretty(interval.start.time()),
                                       pretty(interval.stop.time()),
                                       pretty(interval.total)),
                    padding + '  ')
                if display_notes:
                    p = padding + '    '
                    for x in interval.note.splitlines():
                        out(x, p)

        for key in sorted(container._data.keys()):
            value = container._data[key]
            self.print_container(value, padding + '  ',
                                 display_intervals,
                                 display_notes)


def parse_reporter_kwargs(opts):
    kwargs = {}
    if opts.date_filter is not None:
        start, stop = estimate_startstop(opts.date_filter)
    else:
        start, stop = estimate_startstop('week')
    kwargs.update(date_start=start,
                  date_end=stop,
                  display_intervals=opts.display_intervals,
                  display_notes=opts.display_notes,
                  project_filter=opts.project_filter.split(','))

    return kwargs


def main():
    import os
    import optparse
    import ConfigParser

    parser = optparse.OptionParser()
    parser.add_option('--date-filter', dest='date_filter',
                      help='Date range for bookings to watch for, dates '
                           'must be in YYYY-MM-DD format and can be one '
                           'date or start_date:stop_date.  Values such as '
                           '"all", "week", "today", or "yesterday" are '
                           'also valid.  In addition, it is possible to '
                           'specify an english month word or abbreviation of '
                           'an english month word... the year will '
                           'be assumed to be the current year.  Default date '
                           'filter is "week" which list all entries so far '
                           'this current week starting with Monday')
    parser.add_option('-i', '--display-intervals',
                      action='store_true',
                      default=False,
                      dest='display_intervals',
                      help='Show all bookings')
    parser.add_option('-n', '--display-notes',
                      action='store_true',
                      default=False,
                      dest='display_notes',
                      help='Show all interval notes, only works in '
                           'combination with -i')
    parser.add_option('--project-filter', dest='project_filter',
                      default='',
                      help='Comma-separated list of projects')
    parser.add_option('-d', '--debug', dest='debug',
                      action='store_true',
                      default=False,
                      help='Show debugging output')

    (opts, args) = parser.parse_args()

    if opts.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    configfilename = find_config_file('config.ini')
    config = None
    if not configfilename:
        logger.warn("Couldn't open file %r" % configfilename)
    else:
        logger.info('Loading config file: %r' % configfilename)
        config = ConfigParser.ConfigParser()
        config.read(configfilename)

    tracker = TimeTracker()
    if config is not None and \
           config.has_option('General', 'default_project') and \
           config.get('General', 'default_project').strip():
        prj = config.get('General', 'default_project')
        prj = '/'.join([x.strip() for x in prj.split('/')
                        if x.strip()])
        tracker.default_project = prj

    if len(args) == 0 and config is not None:
        for section in config.sections():
            if section == 'File Group' or section.startswith('File Group:'):
                logger.info('Handling file group %r' % section)
                args = []
                base_dir = config.get(section, 'base_dir')
                r = re.compile(config.get(section, 'filename_match'))
                for x in os.listdir(base_dir):
                    if r.match(x) is not None:
                        args.append(os.path.join(base_dir, x))

                kwargs = {}
                if config.has_option(section, 'parser_name'):
                    kwargs['parser_name'] = config.get(section, 'parser_name')
                tracker.parse(args, **kwargs)

    reporter = TrackerReporter(tracker)
    reporter.print_results(**parse_reporter_kwargs(opts))

if __name__ == '__main__':
    main()

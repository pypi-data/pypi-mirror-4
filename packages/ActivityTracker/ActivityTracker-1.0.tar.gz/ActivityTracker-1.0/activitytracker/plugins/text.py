# text.py is a legacy module used to deal with text files.
# It used to be a separate system and hasn't been refactored to
# reuse code from ActivityTracker proper.

import calendar
import csv
import datetime
import os
import re
import sys
import time
from activitytracker.base import (AbstractFileParser, Interval,
                                  find_config_file)

namespace = {}
configfilename = find_config_file('textconfig')
if configfilename:
    execfile(configfilename, namespace)

BASEDIR = namespace['BASEDIR']
CLIENT_MAPPINGS = namespace['CLIENT_MAPPINGS']
FANCY_CLIENT_MAPPINGS = namespace['FANCY_CLIENT_MAPPINGS']
ACTION_MAPPINGS = namespace['ACTION_MAPPINGS']
for action in ACTION_MAPPINGS.keys():
    exprs = ACTION_MAPPINGS[action]
    regexes = []
    for expr in exprs:
        regexes.append(re.compile(expr, re.IGNORECASE))
    ACTION_MAPPINGS[action] = regexes

RE_JOURNAL_FILE = re.compile('^month-([a-zA-Z]*)-([0-9]*).txt$')
RE_DAY_BEGINS = re.compile('[dD][aA][yY]: *([a-zA-Z]*) *([0-9][0-9]?) *'
                           ', *([0-9][0-9][0-9][0-9]).*')
RE_TIME = re.compile('([0-9][0-9]?):([0-9][0-9]?)([ap]m)? *')
RE_ONLY_TIME = re.compile('^([0-9][0-9]?):([0-9][0-9]?)([ap]m)? *$')
RE_TRAILING_HOURS = re.compile(': *[0-9]*hr')
RE_STOPPED = re.compile(' +stopped +[a-zA-Z ]*([0-9][0-9]?):([0-9][0-9]?)'
                        '([ap]m)? *')
RE_NOT_BILLABLE = re.compile(' *not? *bill(able)?')
RE_DATE = re.compile('([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])')

MONTHS = [None, 'january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']

STATE_NONE = 0
STATE_JUST_READ_TIME = 1

ONE_DAY = datetime.timedelta(days=1)


class Client(object):

    def __init__(self, name):
        self.name = name
        self.projects = {'NO PROJECT': Project('NO PROJECT')}

    def clone(self):
        client = Client(self.name)
        client.projects = self.projects
        return client

    @property
    def bookings(self):
        bookings = BookingContainer()
        for project in self.projects.values():
            bookings += project.bookings
        return bookings


class Project(object):

    def __init__(self, name):
        self.name = name
        self.bookings = BookingContainer()

    def clone(self):
        prj = Project(self.name)
        prj.bookings = self.bookings.clone()
        return prj


class Booking(object):

    def __init__(self, start, stop, comment=''):
        self.start = start
        self.stop = stop
        self.comment = comment

    @property
    def time(self):
        return self.stop - self.start

    def clone(self):
        return Booking(self.start, self.stop, self.comment)

    @property
    def billable(self):
        return RE_NOT_BILLABLE.search(self.comment) is None


class BookingContainer(list):

    def __init__(self, initlist=None):
        self.__total_time = datetime.timedelta()
        self.__total_billable_time = datetime.timedelta()
        if initlist is not None:
            super(BookingContainer, self).__init__(initlist)
            for x in initlist:
                self._add_time(x)
        else:
            super(BookingContainer, self).__init__()

    def _add_time(self, booking):
        self.__total_time += booking.time
        if booking.billable:
            self.__total_billable_time += booking.time

    @property
    def total_time(self):
        return self.__total_time

    @property
    def total_billable_time(self):
        return self.__total_billable_time

    def append(self, x):
        if not isinstance(x, Booking):
            raise TypeError('object is not of type "Booking"')
        self._add_time(x)
        return list.append(self, x)

    def insert(self, index, x):
        self._add_time(x)
        return list.insert(self, index, x)

    def __iadd__(self, other):
        for x in other:
            self._add_time(x)
        return list.__iadd__(self, other)

    def clone(self):
        container = BookingContainer()
        for booking in self:
            container.append(booking.clone())
        return container


def fancy_datetime(d):
    date_format = '%B %d, %Y (%A)'
    time_format = '%I:%M%p'
    tm = d.strftime(time_format).lower()
    if tm.startswith('0'):
        tm = tm[1:]
    if isinstance(d, datetime.datetime):
        return d.strftime(date_format) + ' at ' + tm
    elif isinstance(d, datetime.date):
        return d.strftime(date_format)
    elif isinstance(d, datetime.time):
        return tm


def last_monthday(dt):
    t = dt
    while t.month == dt.month:
        t += ONE_DAY
    t -= ONE_DAY

    return t


def fancy_booking_totals(bookings):
    total = bookings.total_time
    billable = bookings.total_billable_time
    nonbillable = total - billable
    if nonbillable:
        extra = ' [%s *]' % fancy_time_amount(nonbillable)
    else:
        extra = ''
    return '%s%s' % (fancy_time_amount(total),
                     extra)


def fancy_time_amount(total):
    hours = (total.days * 24.0) + (total.seconds / 3600.0)
    return '%s hrs' % hours


def first_weekday(d):
    checking = d
    while calendar.weekday(checking.year,
                           checking.month,
                           checking.day) != calendar.firstweekday():
        checking -= ONE_DAY
    return checking


class Processor(object):

    def __init__(self):
        self.state = STATE_NONE
        self.clients = {}

        self.current_date = None
        self.actions = {}

        self.first_day = None
        self.last_day = None

        self.last_comments = []

    def _start_day(self, date):
        if getattr(self, 'start_time', None) is not None \
               and getattr(self, 'last_funny_datetime', None) is not None:
            start = datetime.datetime.combine(self.current_date,
                                              self.start_time)
            end = datetime.datetime.combine(self.current_date,
                                            self.last_funny_datetime.time())
            booking = Booking(start, end, '\n'.join(self.last_comments))
            if getattr(self, 'last_project', None) is not None:
                self.last_project.bookings.append(booking)
            elif getattr(self, 'last_client', None) is not None:
                project = self.last_client.projects['NO PROJECT']
                project.bookings.append(booking)
        if self.first_day is None or date < self.first_day:
            self.first_day = date
        if self.last_day is None or date > self.last_day:
            self.last_day = date

        self.current_date = date

        self.last_time = None
        self.start_time = None
        self.last_interval = None
        self.last_client = None
        self.last_project = None
        self.last_funny_datetime = None
        self.last_comments = []

    def _journal_file(self, month, year):
        m = MONTHS[month]
        m = m[0].upper() + m[1:]
        return os.path.join(BASEDIR, 'month-%s-%s.txt' % (m, year))

    def _handle_client_project(self, v):
        client, project_name = client_and_project(v)
        client = CLIENT_MAPPINGS.get(client, client)

        client_obj = self.clients.get(client, Client(client))
        self.clients[client] = client_obj
        self.last_client = client_obj
        if project_name is not None:
            projects = client_obj.projects
            project = projects.get(project_name, Project(project_name))
            projects[project_name] = project
            self.last_project = project
        else:
            self.last_project = None

    def process(self, month, year):
        if isinstance(month, basestring):
            month = MONTHS.index(month.lower())
        if isinstance(year, basestring):
            year = int(year)

        f = open(self._journal_file(month, year), 'r')
        try:
            self.process_input(f)
        finally:
            f.close()

    def process_input(self, f):
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            for action, exprs in ACTION_MAPPINGS.items():
                for expr in exprs:
                    if expr.search(stripped) is not None:
                        day = self.actions.get(self.current_date, {})
                        self.actions[self.current_date] = day
                        category = day.get(action, [])
                        day[action] = category
                        category.append(stripped)

            record_comment = True
            if self.state is STATE_JUST_READ_TIME:
                self.last_comments = []
                if not stripped.startswith('-'):
                    self._handle_client_project(stripped)
                    record_comment = False

            self.state = STATE_NONE
            m = RE_ONLY_TIME.match(stripped)
            if m is not None:
                self.state = STATE_JUST_READ_TIME
                self._handle_time(stripped)
                record_comment = False
            if m is None:
                m = RE_STOPPED.search(stripped)
                if m is not None:
                    self._handle_time(stripped, True)
                    record_comment = False
            if m is None:
                m = RE_DAY_BEGINS.search(stripped)
                if m is not None:
                    year = int(m.group(3))
                    day = int(m.group(2))
                    month = MONTHS.index(m.group(1).lower())
                    date = datetime.date(year, month, day)
                    self._start_day(date)
                    record_comment = False
            if m is None:
                m = RE_TIME.search(stripped)
                if m is not None:
                    comb = datetime.datetime.combine
                    self.last_funny_datetime = comb(self.current_date,
                                                    parse_time(stripped))
                    record_comment = False

            if record_comment:
                self.last_comments.append(stripped)

    def _handle_time(self, v, stopped=False):
        tm = parse_time(v.strip())
        if self.start_time is None:
            self.start_time = tm
            self.last_project = None
            self.last_client = None
        else:
            start = datetime.datetime.combine(self.current_date,
                                              self.start_time)
            end = datetime.datetime.combine(self.current_date,
                                            tm)
            if self.last_funny_datetime is not None and not stopped:
                comb = datetime.datetime.combine
                end = comb(self.current_date,
                           self.last_funny_datetime.time())
            booking = Booking(start, end, '\n'.join(self.last_comments))
            if self.last_project is not None:
                self.last_project.bookings.append(booking)
            elif self.last_client is not None:
                project = self.last_client.projects['NO PROJECT']
                project.bookings.append(booking)

            self.last_interval = end - start
            if stopped:
                self.start_time = None
            else:
                self.start_time = tm

            if self.last_interval.days < 0:
                raise ValueError("Error on day: %s (%s, %s)" % \
                                 (fancy_datetime(self.current_date),
                                  start,
                                  end))

            self.last_funny_datetime = None

        self._last_time = tm

    def _build_filtered(self, client_filter, project_filter,
                        comment_filter,
                        date_start_filter, date_stop_filter):

        class Filtered(object):
            pass

        filtered = Filtered()
        filtered.clients = {}
        filtered.earliest = None
        filtered.latest = None
        filtered.bookings = BookingContainer()
        filtered.first_day = self.first_day
        filtered.last_day = self.last_day
        if date_start_filter is not None:
            filtered.first_day = date_start_filter.date()
        if date_stop_filter is not None:
            filtered.last_day = date_stop_filter.date()

        for client_name in sorted(self.clients.keys()):
            if matches(client_name, client_filter):
                client_obj = self.clients[client_name].clone()
                updated_projects = {}
                for project_name in sorted(client_obj.projects.keys()):
                    if matches(project_name, project_filter):
                        orig_project = client_obj.projects[project_name]
                        updated_project = orig_project.clone()
                        updated_project.bookings = BookingContainer()
                        for booking in orig_project.bookings:

                            if date_start_filter is None or \
                               (booking.start >= date_start_filter and \
                                booking.start <= date_stop_filter and \
                                booking.stop >= date_start_filter and \
                                booking.stop <= date_stop_filter):

                                if comment_filter is None or \
                                   comment_filter.search(booking.comment) \
                                   is not None:

                                    filtered.bookings.append(booking)
                                    updated_project.bookings.append(booking)
                                    if filtered.earliest is None or \
                                           booking.start < filtered.earliest:
                                        filtered.earliest = booking.start
                                    if filtered.latest is None or \
                                           booking.stop > filtered.latest:
                                        filtered.latest = booking.stop

                        if len(updated_project.bookings) > 0:
                            updated_projects[project_name] = updated_project
                if len(updated_projects) > 0:
                    filtered.clients[client_name] = client_obj
                client_obj.projects = updated_projects

        filtered.actions = {}
        for day in sorted(self.actions.keys()):
            categories = self.actions[day]
            if day >= filtered.first_day and day <= filtered.last_day:
                if categories:
                    filtered.actions[day] = categories

        return filtered

    def show_results(self, out, client_filter=None, project_filter=None,
                     date_start_filter=None, date_stop_filter=None,
                     report_type=None,
                     comment_filter=None,
                     display_bookings=False,
                     display_bookings_comments=False):

        if report_type is None:
            report_type = 'date'
        else:
            report_type = report_type.lower()

        filtered = self._build_filtered(client_filter, project_filter,
                                        comment_filter,
                                        date_start_filter, date_stop_filter)

        if report_type == 'csv':
            writer = csv.writer(sys.stdout)
            writer.writerow(['Client', 'Project', 'Date',
                             'Duration (hrs)', 'Comments'])
            for client_name in sorted(filtered.clients.keys()):
                client = filtered.clients[client_name]
                projects = client.projects
                for project_name in projects:
                    project = projects[project_name]
                    for booking in project.bookings:
                        tm = booking.time
                        tm = tm.seconds / 60.0 / 60.0
                        writer.writerow([client_name,
                                         project_name,
                                         booking.start.date(),
                                         tm,
                                         booking.comment])
        else:
            print >> out, "Filter:"
            if client_filter is not None:
                print >> out, "  Client(s): %s" % str(client_filter)
            if project_filter is not None:
                print >> out, "  Project(s): %s" % str(project_filter)
            if date_start_filter is not None:
                print >> out, "  Start Date: %s" \
                      % fancy_datetime(date_start_filter)
            if date_stop_filter is not None:
                print >> out, "  Stop Date: %s" \
                      % fancy_datetime(date_stop_filter)
            print >> out

            if filtered.earliest is None:
                earliest = 'N/A'
            else:
                earliest = fancy_datetime(filtered.earliest)
            print >> out, "Earliest: %s" % earliest
            if filtered.earliest is None:
                latest = 'N/A'
            else:
                latest = fancy_datetime(filtered.latest)
            print >> out, "Latest: %s" % latest
            if filtered.earliest is None or filtered.latest is None:
                tracked = 'N/A'
            else:
                days = (filtered.latest - filtered.earliest).days
                if days > 365:
                    tracked = '%.2f years' % (days / 365.0)
                else:
                    seconds = (filtered.latest - filtered.earliest).seconds
                    minutes = seconds / 60.0
                    hours = minutes / 60.0
                    extra_days = hours / 24.0
                    tracked = '%.1f days' % (days + extra_days)
            print >> out, "Total Time Tracked: %s" % tracked

            print >> out

            print >> out, 'Dates:'
            days = {}
            for client_name, client in filtered.clients.items():
                for project_name, project in client.projects.items():
                    for booking in project.bookings:
                        date = booking.start.date()
                        day = days.get(date, {'clients': {},
                                              'bookings': BookingContainer()})
                        days[date] = day
                        day['bookings'].append(booking)

                        default = {'projects': {},
                                   'bookings': BookingContainer()}
                        client_dict = day['clients'].get(client_name, default)
                        day['clients'][client_name] = client_dict
                        client_dict['bookings'].append(booking)

                        projects = client_dict['projects']
                        project_bookings = projects.get(project_name,
                                                        BookingContainer())
                        projects[project_name] = project_bookings

                        project_bookings.append(booking)

            print >> out
            for date in sorted(days.keys()):
                day = days[date]
                print >> out, "  %s (total: %s)" \
                      % (fancy_datetime(date),
                         fancy_booking_totals(day['bookings']))
                for client_name in sorted(day['clients'].keys()):
                    client = day['clients'][client_name]
                    print >> out, '    %s (total: %s)' \
                          % (FANCY_CLIENT_MAPPINGS[client_name],
                             fancy_booking_totals(client['bookings']))
                    for project_name in sorted(client['projects'].keys()):
                        bookings = client['projects'][project_name]
                        print >> out, '      %s (%s)' \
                              % (project_name, fancy_booking_totals(bookings))
                        if display_bookings:
                            for booking in bookings:
                                print >> out, '        %s to %s (%s)' \
                                      % (fancy_time(booking.start),
                                         fancy_time(booking.stop),
                                         fancy_time_amount(booking.stop -
                                                           booking.start))
                                if display_bookings_comments:
                                    if booking.comment.strip():
                                        lines = booking.comment.split('\n')
                                        for line in lines:
                                            print "          %s" % line

                print >> out

            print >> out, "Clients (total: %s):" \
                  % fancy_booking_totals(filtered.bookings)
            print >> out
            for client in sorted(filtered.clients.keys()):
                client_obj = filtered.clients[client]
                all_bookings = client_obj.bookings
                print >> out, '  %s (total: %s)' \
                      % (FANCY_CLIENT_MAPPINGS.get(client, client),
                         fancy_booking_totals(all_bookings))
                projects = client_obj.projects
                for project_name in sorted(projects.keys()):
                    project = projects[project_name]
                    print >> out, '    %s: %s' \
                          % (project_name,
                             fancy_time_amount(project.bookings.total_time))

                print >> out


def show_bookings(out, prefix, project, show_comments):
    print >> out, '%sBookings:' % prefix
    days = {}
    for booking in project.bookings:
        day = days.get(booking.start.date(), BookingContainer())
        days[booking.start.date()] = day
        day.append(booking)

    for day in sorted(days.keys()):
        bookings = days[day]
        print "  %s%s (subtotal: %s)" % (prefix, day,
                                         fancy_booking_totals(bookings))

        for booking in bookings:
            hours = (booking.stop - booking.start).seconds / 3600.0
            fancy = '%s to %s (%s hrs)' % (fancy_time(booking.start),
                                           fancy_time(booking.stop), hours)
            if booking.billable:
                asterisk = ''
            else:
                asterisk = ' *'
            print "    %s%s%s" % (prefix, fancy, asterisk)
            if show_comments:
                for line in booking.comment.split('\n'):
                    print "      %s%s" % (prefix, line)


def fancy_time(v):
    if isinstance(v, datetime.datetime):
        v = v.time()
    s = v.strftime('%I:%M%p')
    if s.startswith('0'):
        s = s[1:]
    return s.lower()


def matches(v, lst):
    if lst is None:
        return True
    for x in lst:
        if v.find(x) > -1:
            return True


def parse_time(v):
    m = RE_STOPPED.search(v)
    if m is None:
        m = RE_ONLY_TIME.match(v)
    if m is None:
        m = RE_TIME.search(v)
    hour = int(m.group(1))
    minute = int(m.group(2))
    if m.group(3) == 'pm':
        if hour != 12:
            hour += 12
    if m.group(3) == 'am':
        if hour == 12:
            hour = 0
    tm = datetime.time(hour, minute)
    return tm


def client_and_project(v):
    pos = v.find(':')
    if pos == -1:
        pos = v.find('/')

    if pos != -1:
        client = v[:pos].strip()
        project_name = v[pos + 1:].strip()
    else:
        client = v.strip()
        project_name = None

    if project_name is not None and project_name.strip() == '':
        project_name = None
    client = client.lower()
    if project_name is not None:
        project_name = project_name.lower()
        m = RE_TRAILING_HOURS.search(project_name)
        if m is not None:
            project_name = project_name[:m.start()]
        pos = project_name.find('[not billing]')
        if pos > -1:
            project_name = project_name.replace('[not billing]', '').strip()
        if project_name[-1].endswith(':'):
            project_name = project_name[:-1]

    return (client, project_name)


def _guess_startstop(datestr):
    if not datestr:
        raise ValueError('datestr cannot be empty')

    if datestr == 'all':
        start = None
        stop = None
    elif datestr == 'today':
        start = datetime.datetime.now()
        start = datetime.datetime(start.year, start.month, start.day)
        stop = datetime.datetime(start.year, start.month, start.day, 23, 59)
    elif datestr == 'yesterday':
        start = datetime.datetime.now() - ONE_DAY
        start = datetime.datetime(start.year, start.month, start.day)
        stop = datetime.datetime(start.year, start.month, start.day, 23, 59)
    elif datestr == 'week':
        start = datetime.datetime.now()
        start = datetime.datetime(start.year, start.month, start.day)
        stop = datetime.datetime(start.year, start.month, start.day, 23, 59)
        start = first_weekday(start)
    elif datestr == 'month':
        start = datetime.datetime.now()
        start = datetime.datetime(start.year, start.month, 1)
        stop = last_monthday(start)
        stop = datetime.datetime(stop.year, stop.month, stop.day, 23, 59)
    elif datestr == 'year':
        start = datetime.datetime.now()
        start = datetime.datetime(start.year, 1, 1)
        stop = datetime.datetime.now()
        stop = datetime.datetime(stop.year, stop.month, stop.day, 23, 59)
    else:
        if RE_DATE.match(datestr) is not None:
            start = datetime.datetime(*time.strptime(datestr, '%Y-%m-%d')[:3])
            stop = datetime.datetime(start.year, start.month,
                                     start.day, 23, 59)
        else:
            month_index = -1
            for pos, month in enumerate(MONTHS):
                if month is not None and month.startswith(datestr):
                    month_index = pos
                    break
            if month_index == -1:
                raise ValueError("Couldn't derive a date value from %r"
                                 % datestr)

            start = datetime.datetime.now()
            start = datetime.datetime(start.year, month_index, 1)
            stop = last_monthday(start)
            stop = datetime.datetime(stop.year, stop.month, stop.day, 23, 59)

    return start, stop


def parse_startstop(date_filter):
    """
    Takes a date range that understands common aliases and returns the start
    and stop times as a tuple.
    """

    date_filter = date_filter or ''
    date_filter = date_filter.strip().lower()
    if not date_filter:
        date_filter = 'week'

    datestrs = date_filter.split(':')
    start_datestr = datestrs[0]
    stop_datestr = ''
    if len(datestrs) > 1:
        stop_datestr = datestrs[1]

    start, stop1 = _guess_startstop(start_datestr)
    if stop_datestr:
        start2, stop = _guess_startstop(stop_datestr)
    else:
        stop = stop1

    return start, stop


class TextFileParser(AbstractFileParser):

    def parse_input(self, input):
        processor = Processor()
        processor.process_input(input)
        for client_name, client in processor.clients.items():
            for project_name, project in client.projects.items():
                new_prj = self.projects[client_name + '/' + project_name]
                for booking in project.bookings:
                    interval = Interval(booking.start,
                                        booking.stop,
                                        booking.comment)
                    new_prj.intervals.append(interval)

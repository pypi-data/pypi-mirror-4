import datetime
import re
import os
import StringIO
import xml.dom

TIME_RE = re.compile(r'([0-9]?[0-9]):([0-9][0-9])(am|pm|)')
DIGITS = '0123456789'

MONTH_NAMES = [None, u'january', u'february', u'march', u'april', u'may',
               u'june', u'july', u'august', u'september', u'october',
               u'november', u'december']
MONTHS = {}
for x, month in enumerate(MONTH_NAMES):
    if month is not None:
        MONTHS[month] = x
        MONTHS[month[:3]] = x
        MONTHS[x] = month


def parse_time(s):
    """Take the given string and pull out a time object representation.

      >>> parse_time('2:00pm')
      datetime.time(14, 0)

      >>> parse_time('1:00')
      datetime.time(1, 0)

      >>> parse_time('3')
      datetime.time(3, 0)

      >>> parse_time('6p')
      datetime.time(18, 0)

      >>> parse_time('abc def 7:32a')
      datetime.time(7, 32)

      >>> parse_time(u'1:30pm foo bar')
      datetime.time(13, 30)

      >>> parse_time('12:15p')
      datetime.time(12, 15)

      >>> parse_time('foobar')
      Traceback (most recent call last):
        ...
      ValueError: Couldn't find a valid time in 'foobar'
    """

    first = -1
    last = -1
    for x, c in enumerate(s):
        if first == -1 and c in DIGITS:
            first = x
        elif first != -1 and c == ' ':
            last = x
            break

    if first == -1:
        raise ValueError("Couldn't find a valid time in %r" % str(s))

    if last == -1:
        last = len(s)

    timestr = str(s[first:last])

    colonpos = timestr.find(':')
    apos = timestr.find('a')
    ppos = timestr.find('p')
    ampmpos = -1
    if apos > -1:
        ampmpos = apos
    elif ppos > -1:
        ampmpos = ppos

    if colonpos > -1:
        endhourpos = colonpos
    elif ampmpos > -1:
        endhourpos = ampmpos
    else:
        endhourpos = len(timestr)

    hour = int(timestr[:endhourpos])
    minute = 0

    if colonpos > -1:
        if ampmpos > -1:
            minute = int(timestr[colonpos + 1:ampmpos])
        else:
            minute = int(timestr[colonpos + 1:])

    if ppos > -1 and hour < 12:
        hour += 12
    elif ppos == -1 and hour == 12:
        hour = 0

    tm = datetime.time(hour, minute)
    return tm


class AbstractFileParser(object):

    def __init__(self, projects, default_project):
        self.projects = projects
        self.default_project = default_project

    def parse_input(self, input):
        raise NotImplementedError()


class StandardFileParser(AbstractFileParser):
    """Activitytracker2 has introduced a new format for defining dates, times,
    etc.  This new format protocol is referred to as the 'standard' format.
    Any time a pre-activitytracker2 format is referred to it will be called
    the 'legacy' format.
    """

    GENERAL_COMMAND_RE = re.compile(r'\[([.a-zA-Z0-9:/\-_ #]*?)\]')
    TIME_RE = TIME_RE
    FULL_DATE_RE = re.compile(r'Today: [a-zA-Z]*?, *([0-9][0-9]?) '
                              r'*([a-zA-Z]*) *([0-9]*)')

    default_project = None

    def _dt(self, tm, date=None):
        if date == None:
            date = self.current_date
        return datetime.datetime.combine(date, tm)

    def handle_interval(self, tm):
        note_list = [x.strip() for x in self.current_note]
        note = '\n'.join(note_list)
        note = note.strip()
        interval = Interval(self._dt(self.last_time),
                            self._dt(tm),
                            note)
        self.projects[self.current_project_name].intervals.append(interval)
        self.current_note = []

    def handle_command(self, cmd, at_beginning=False):
        # check for a time cmd at beginning of the cmd string
        result = self.TIME_RE.search(cmd)
        if result and result.start() == 0:
            spanstart, spanstop = result.span()

            tm = parse_time(cmd)

            if not at_beginning and self.last_time is not None:
                self.handle_interval(tm)
                self.last_time = None
            elif self.last_time is not None:
                self.handle_interval(tm)
                self.last_time = tm
            else:
                self.last_time = tm

            if spanstop - spanstart < len(cmd):
                rest = cmd[spanstop:].strip()
                parts = [x.strip() for x in rest.split('/')]
                self.current_project_name = '/'.join(parts)
            elif self.default_project is not None \
                     and self.current_project_name is None:
                self.current_project_name = self.default_project

    def setup_date(self, date):
        self.current_date = date

    def get_data(self, input):
        raise NotImplementedError()

    def parse_input(self, input):
        """The input argument is required to be a file-like object.
        """

        data = self.get_data(input)
        if data is None:
            return

        self.last_time = None
        self.current_date = None
        self.current_note = []
        self.current_project_name = None

        io = StringIO.StringIO(data)

        for line in io.readlines():
            line = line.rstrip()
            result = self.GENERAL_COMMAND_RE.search(line)
            if result and len(result.groups()) > 0:
                at_beginning = result.start() == 0
                self.handle_command(result.groups()[0],
                                    at_beginning)
                if not at_beginning:
                    self.current_note.append(line)

            if not result:
                result = self.FULL_DATE_RE.search(line)
                if result:
                    sday, smonth, syear = result.groups()
                    day = int(sday)
                    month = MONTHS[smonth.lower()]
                    year = int(syear)
                    date = datetime.date(year, month, day)
                    self.setup_date(date)

            if not result:
                self.current_note.append(line)

        now = datetime.datetime.now()
        if self.current_date == now.date() \
               and self.current_project_name is not None \
               and self.last_time is not None:
            tm = now.time()
            mins = int((tm.minute + 7.5) // 15 * 15)
            if mins >= 60:
                mins = 45
            tm = tm.replace(minute=mins, second=0, microsecond=0)
            self.handle_interval(tm)


class Interval(object):
    """Some period of time with start and end datetime's and an optional
    node.

      >>> from datetime import datetime
      >>> Interval(datetime(2003, 2, 9), datetime(2003, 2, 12))
      <Interval start=2003-02-09 00:00:00; stop=2003-02-12 00:00:00>

      >>> Interval(datetime(2003, 2, 9), datetime(2003, 2, 12)).total
      datetime.timedelta(3)
    """

    start = None
    stop = None
    note = None

    def __init__(self, start, stop, note=None):
        self.start = start
        self.stop = stop
        self.note = note or u''

        if stop < start:
            raise ValueError('The start date cannot come after the stop date '
                             '(start=%s; stop=%s)' % (str(start), str(stop)))

    @property
    def total(self):
        return self.stop - self.start

    def __str__(self):
        return '<Interval start=%s; stop=%s>' % (str(self.start),
                                                 str(self.stop))
    __repr__ = __str__


def flatten_to_text(*nodes):
    """Extract as much text from the node and children nodes (recursively)
    as possible.

      >>> from xml.dom import minidom

      >>> dom = minidom.parseString('<root>foobar</root>')
      >>> flatten_to_text(dom)
      u'foobar'

      >>> dom = minidom.parseString('<abc>bar<def>hello world</def>foo</abc>')
      >>> flatten_to_text(dom)
      u'barhello worldfoo'
      >>> flatten_to_text(dom.childNodes)
      u'barhello worldfoo'

      >>> dom1 = minidom.parseString('<abc>foo</abc>')
      >>> dom2 = minidom.parseString('<abc>bar</abc>')
      >>> flatten_to_text(dom1, dom2)
      u'foobar'

    """

    s = u''
    for node in nodes:
        if isinstance(node, xml.dom.minidom.Text):
            s += node.wholeText
        else:
            if isinstance(node, (list, tuple, xml.dom.minicompat.NodeList)):
                subnodes = node
            else:
                subnodes = node.childNodes

            for x in subnodes:
                s += flatten_to_text(x)

    return s


def find_config_file(fname):
    currentdir = os.getcwd()
    fullpath = os.path.join(currentdir, '.activitytracker', fname)
    if os.path.isfile(fullpath):
        return fullpath

    homedir = os.path.expanduser('~')
    fullpath = os.path.join(homedir, '.activitytracker', fname)
    if os.path.isfile(fullpath):
        return fullpath

    return None

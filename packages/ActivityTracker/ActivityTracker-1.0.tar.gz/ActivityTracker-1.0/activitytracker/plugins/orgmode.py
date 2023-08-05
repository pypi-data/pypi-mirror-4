from activitytracker import base
import datetime
import re


class EmacsOrgModeParser(base.AbstractFileParser):
    """A parser that understands OrgMode-formatted text files.  Any
    heading marked with a "book" tag and a timestamp as the next
    line will be treated as a time interval.
    """

    heading_re = re.compile('([*]+)(.*)')
    tags_re = re.compile('(.*):([a-zA-Z0-9]+):')
    date_re = re.compile('<([0-9]+)-([0-9]+)-([0-9]+) [a-zA-Z]* '
                         '([0-9]+):([0-9]+)(-([0-9]+):([0-9]+))?>')

    def parse_input(self, input):
        task = None
        extra = []
        for line in input:
            line = line.rstrip()
            headingmatch = self.heading_re.match(line)
            if not headingmatch:
                extra.append(line)
                continue

            heading = headingmatch.group(2).strip()
            tags = []
            tagsmatch = self.tags_re.match(heading)
            if tagsmatch:
                heading = tagsmatch.group(1).strip()
                tags = [x for x in tagsmatch.group(2).split(':') if x.strip()]
            if 'book' in tags:
                if task:
                    self.handle(task, extra)
                task = heading
                extra = []
            else:
                extra.append(line)

        if task:
            self.handle(task, extra)

    def handle(self, task, extra):
        m = self.date_re.match(extra[0])
        if not m:
            return

        start = [m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)]
        stop = [m.group(1), m.group(2), m.group(3), m.group(7), m.group(8)]
        if stop[3] is None:
            stop[3] = int(start[3]) + 1
            stop[4] = 0

        start = datetime.datetime(*map(int, start))
        stop = datetime.datetime(*map(int, stop))

        task = '/'.join([x.strip() for x in task.split('/') if x.strip()])
        note = '\n'.join([x for x in extra[1:] if x.strip()])
        interval = base.Interval(start, stop, note)
        self.projects[task].intervals.append(interval)

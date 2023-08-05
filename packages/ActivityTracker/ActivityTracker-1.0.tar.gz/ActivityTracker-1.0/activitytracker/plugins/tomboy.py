from activitytracker import base
import xml.dom.minidom


class TomboyFileParser(base.StandardFileParser):
    """A parser that uses the standard format but knows how to deal with
    tomboy note files.
    """

    def get_data(self, input):
        dom = xml.dom.minidom.parse(input)
        titletext = base.flatten_to_text(dom.getElementsByTagName('title')[0])

        # see FULL_DATE_RE definition to see what valid titles can be for
        # a tomboy note to be parsed
        if self.FULL_DATE_RE.match(titletext) is None:
            return None

        els = dom.getElementsByTagName('note-content')
        text = base.flatten_to_text(els[0])
        return text

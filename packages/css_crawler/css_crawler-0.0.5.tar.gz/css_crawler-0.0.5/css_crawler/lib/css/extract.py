import htmlcolor

from css_crawler.lib import log
import capture
from itertools import izip, repeat


class ColorExtractor:

    PROPERTY_MAP = {'background-color': (None, 'background-color'),
                    'background': (0, 'background-color'),
                    'color': (None, 'color'),

                    }

    BORDER_COLOR_PROPERTIES = ['border-color',
                               'border-top-color',
                               'border-bottom-color',
                               'border-left-color',
                               'border-right-color']

    PROPERTY_MAP.update(dict(izip(
        BORDER_COLOR_PROPERTIES, repeat((None, 'border-color')))))

    BORDER_PROPERTIES = ['border',
                         'border-top',
                         'border-bottom',
                         'border-left',
                         'border-right']

    PROPERTY_MAP.update(dict(izip(
        BORDER_PROPERTIES, repeat((-1, 'border-color')))))

    def __init__(self, log=log, stylesheets=[]):
        self._log = log
        self._stylesheets = stylesheets
        self._color_parser = htmlcolor.Parser()
        self.parsed_colors = {
            'background-color': {},
            'color': {},
            'border-color': {}
        }

    def extract_colors(self):
        for stylesheet in self._stylesheets:
            self._extract_colors(stylesheet)

    def _parse_color_and_update(self, color, key, selectors):
        try:
            self.parsed_colors[key].setdefault(
                '#%02x%02x%02x' % self._color_parser.parse(str(color)),
                []).extend([s.selectorText for s in selectors])
        except (ValueError, KeyError) as e:
            self._log.debug(
                'Value %s is not a valid css color: %r\n---\n%r',
                color, selectors, e)

    def _extract_colors(self, stylesheet):

        for rule in (r for r in stylesheet.cssRules if hasattr(r, 'style')):
            for css_property, (split_index, css_key) in self.PROPERTY_MAP.iteritems():
                color = rule.style[css_property].strip()
                self._log.info(color)
                if color and split_index is not None:
                    self._log.info(color.split())
                    color = color.split()[split_index]

                if color:
                    self._log.debug('found "%s": %s', css_property, color)
                    self._parse_color_and_update(color, css_key,
                                                 rule.selectorList)


def capture_and_extract_colors(url, log=log):
    ua = ('Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) '
          'Gecko/20070515 Firefox/2.0.0.4')
    css_capture = capture.CSSCapture(ua, log)
    url, stylesheets = css_capture.capture(url)
    color_extractor = ColorExtractor(log, stylesheets)
    color_extractor.extract_colors()
    return url, color_extractor.parsed_colors

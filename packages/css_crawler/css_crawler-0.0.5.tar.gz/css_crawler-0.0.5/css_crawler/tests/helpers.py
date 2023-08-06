import os.path
import cssutils
from css_crawler.lib.css.extract import ColorExtractor
import os
import logging
log = logging.getLogger()


def load_stylesheet_file(filename):
    parser = cssutils.CSSParser()
    stylesheet = parser.parseFile(filename)
    return cssutils.resolveImports(stylesheet)


def load_stylesheet_string(css_text, href=None):
    parser = cssutils.CSSParser()
    stylesheet = parser.parseString(css_text, href=href)
    return cssutils.resolveImports(stylesheet)


def extract_color_from_stylesheets(stylesheets):
    color_extractor = ColorExtractor(log, stylesheets)
    color_extractor.extract_colors()
    return color_extractor.parsed_colors


def no_stylesheet_fetcher(url, ua='', log=log):
    return None


# TODO: use pymox

class FakeInfo():

    def gettype(self):
        return "text/css"

    def getparam(self, key):
        return 'utf-8'


class FakeResponse(object):

    def __init__(self, url, content):
        self.url = url
        self.content = content
        self._info = FakeInfo()

    def geturl(self):
        return self.url

    def read(self):
        return self.content

    def info(self):
        return self._info


def base_stylesheet_fetcher(url, ua='', log=log):
    uri, ext = os.path.splitext(url)

    if ext == '.css':
        return FakeResponse(url, """/*empty CSS""")

    else:
        return FakeResponse(url, """<html><head>
    <link type="text/css" rel="stylesheet" href="test.css"/>
    </head><body/></html>
    """)

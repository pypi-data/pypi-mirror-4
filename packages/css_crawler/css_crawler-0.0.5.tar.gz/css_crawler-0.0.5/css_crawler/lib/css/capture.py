import urlparse
import re
import os
import cStringIO

import cssutils
from nagare.namespaces.xhtml_base import Renderer

import fetch
from css_crawler.lib import log

CHARSET_PATTERN = re.compile('^@charset.*$', re.MULTILINE | re.IGNORECASE)


class CSSCapture(object):

    # It is inspired by CSSCapture but use lxml as HTMLParser and solves
    # problem of encoding, for badly included CSS

    #>>> url = 'http://cthedot.de'
    #>>> from cssutils.script import CSSCapture
    #>>> capturer = CSSCapture(ua=None, log=None, defaultloglevel=logging.INFO)
    #>>> url, stylesheetlist = capturer.capture(url)
    #>>> print stylesheetlist
    #[cssutils.css.CSSStyleSheet(
    #    href=u'http://cthedot.de/css/default.css',
    #    media=None, title=None),
    # cssutils.css.CSSStyleSheet(
    #    href=u'http://cthedot.de/static/alternate1.css',
    #    media=None, title=u'red'),
    # cssutils.css.CSSStyleSheet(
    #    href=u'http://cthedot.de/static/alternate2.css',
    #    media=None, title=u'blue')]

    def __init__(self, ua='CSS Crawler', log=log, fetcher=fetch.fetch_url):
        self._ua = ua
        self._log = log
        self._nonparsed = {}
        self._cssparser = cssutils.CSSParser(log=self._log)
        self._url_fetcher = fetcher
        self._css_fetcher = fetch.css_fetcher_factory(self._ua, self._log,
                                                      self._url_fetcher)
        self._cssparser.setFetcher(self._css_fetcher)

    def capture(self, url):
        """
        Capture all stylesheets at given URL's HTML document.
        Any HTTPError is raised to caller.

        url
            to capture CSS from

        Returns ``cssutils.stylesheets.StyleSheetList``.
        """
        self._log.info(u'CAPTURING CSS from URL: %s', url)
        self._nonparsed = {}
        self.stylesheetlist = cssutils.stylesheets.StyleSheetList()

        # used to save inline styles
        pieces = urlparse.urlsplit(url)
        self._filename = os.path.basename(pieces.path)

        # get url content
        url, res = self._do_request(url)
        if not res:
            return url, []

        # fill list of stylesheets and list of raw css
        self._find_stylesheets(url, res.read())

        return res.geturl(), self.stylesheetlist

    def _do_imports(self, parentStyleSheet, base=None):
        """
        handle all @import CSS stylesheet recursively
        found CSS stylesheets are appended to stylesheetlist
        """
        for rule in parentStyleSheet.cssRules:
            if rule.type == rule.IMPORT_RULE:
                self._log.info(u'+ PROCESSING @import:')
                self._log.debug(u'    IN: %s\n', parentStyleSheet.href)
                sheet = rule.styleSheet
                href = urlparse.urljoin(base, rule.href)
                if sheet:
                    self._log.info(u'    %s\n', sheet)
                    self.stylesheetlist.append(sheet)
                    self._do_imports(sheet, base=href)

    def _do_request(self, url):
        """Do an HTTP request

        Return (url, rawcontent)
            url might have been changed by server due to redirects etc
        """
        self._log.debug(u'CSSCapture._do_request URL: %s', url)

        res = self._url_fetcher(url, ua=self._ua, log=self._log)

        if res is None:
            return None, None

        # get real url
        if url != res.geturl():
            url = res.geturl()
            self._log.info('\tURL retrieved: %s', url)

        return url, res

    def _create_stylesheet(self, href=None,
                           media=None,
                           parentStyleSheet=None,
                           title=u'',
                           cssText=None,
                           encoding=None):
        """
        Return CSSStyleSheet read from href or if cssText is given use that.

        encoding
            used if inline style found, same as self.docencoding
        """

        if cssText is None:
            encoding, cssText = self._css_fetcher(href)
            if cssText is None:
                return None
            cssText = CHARSET_PATTERN.sub('', cssText)

        sheet = self._cssparser.parseString(cssText, href=href, media=media,
                                            title=title, encoding=encoding)

        if not sheet:
            return None

        else:
            self._log.info(u'\t%s\n', sheet)
            self._nonparsed[sheet] = cssText
            return sheet

    def _find_stylesheets(self, docurl, doctext):
        """
        parse text for stylesheets
        fills stylesheetlist with all found StyleSheets

        docurl
            to build a full url of found StyleSheets @href
        doctext
            to parse
        """
        tree = Renderer().parse_html(cStringIO.StringIO(doctext))

        sheet = None

        # find any base tag to get effective docurl
        for atts in [elt for elt in tree.xpath('//base')
                     if elt.get('href') is not None]:
            docurl = atts.get('href')

        for atts in [elt for elt in tree.xpath('//link')
                     if (elt.get('type') == 'text/css' or
                         elt.get('rel') == 'stylesheet')]:

            self._log.info(u'+ PROCESSING <link> %r', atts)
            href = urlparse.urljoin(docurl, atts.get(u'href', None))
            sheet = self._create_stylesheet(href=href,
                                            media=atts.get(u'media', None),
                                            title=atts.get(u'title', None))
            if sheet:
                self.stylesheetlist.append(sheet)
                self._do_imports(sheet, base=docurl)

        for atts in [elt for elt in tree.xpath('//style') if
                     elt.get('type', 'text/css') == 'text/css']:

            self._log.info(u'+ PROCESSING <style> %r', atts)
            # convert everything into utf-8 string, we need to remove any
            # @charset rule in order to remove conflicts with cssutils
            text = CHARSET_PATTERN.sub('', atts.text)
            sheet = self._create_stylesheet(
                cssText=text.encode('utf-8', 'ignore'),
                href=docurl,
                media=atts.get(u'media', None),
                title=atts.get(u'title', None))

            if sheet:
                sheet._href = None  # inline have no href!

            if sheet:
                self.stylesheetlist.append(sheet)
                self._do_imports(sheet, base=docurl)

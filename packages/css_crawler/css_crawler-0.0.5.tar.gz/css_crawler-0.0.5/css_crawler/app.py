from __future__ import with_statement

from nagare import presentation, component
from nagare.ajax import YUI_PREFIX

# --------------------------------------------------

import models
from css_crawler.lib.css import extract
from css_crawler.lib import log
from css_crawler.ui.tagcloud.component import TagCloud
from css_crawler.ui.colorpalette.component import ColorPalette
from css_crawler.ui.urlfetcher.component import UrlFetcher


class CrawlerTask(component.Task):

    def __init__(self, app):
        self.url_id = None
        self.app = app

    def go(self, comp):
        if self.url_id is None:
            self.url_id = comp.call(TagCloud(models.URLData.query))

        palette = ColorPalette(self.url_id)
        palette._v_url.viewed += 1
        self.url_id = comp.call(palette)


class FetcherTask(component.Task):

    def __init__(self, callback):
        self.callback = callback

    def go(self, comp):
        url = comp.call(UrlFetcher())
        self.fetch(url)

    def fetch(self, url):
        url, palette = extract.capture_and_extract_colors(url, log)

        if url:
            url_data = models.URLData.get_by_or_init(url=url)
            url_data.palette = palette
            self.callback(url_data.id)


class CSSCrawler(object):

    def __init__(self):
        self.main_task = component.Component(CrawlerTask(self))
        self.fetcher_task = component.Component(
            FetcherTask(self.main_task.answer))


@presentation.render_for(CSSCrawler)
def render(self, h, comp, *args):

    h.head.css_url(YUI_PREFIX + '/reset-fonts/reset-fonts.css')
    h.head.css_url('css/stylesheet.css')

    h.head.javascript_url(YUI_PREFIX + '/yahoo/yahoo-min.js')
    h.head.javascript_url(YUI_PREFIX + '/dom/dom-min.js')
    h.head.javascript_url(YUI_PREFIX + '/event/event-min.js')
    h.head.javascript_url(YUI_PREFIX + '/element/element-min.js')

    h.head.javascript_url('js/script.js')

    h.head << h.head.title('CSS Crawler')

    with h.body(class_='crawler-background'):
        with h.div(class_='main-content'):

            with h.div(class_='form'):
                h << self.fetcher_task

            h << self.main_task

            h << h.div(class_='sep')

    return h.root


# meaningful urls
@presentation.init_for(CSSCrawler, "(len(url) == 1)")
def init(self, url, *args):

    # URL is the short_url created previously
    short_url = url[0]

    url_data = models.URLData.get_by(short_url=short_url)
    if url_data is None:
        raise presentation.HTTPNotFound()

    url_data.viewed += 1
    self.main_task().url_id = url_data.id

# ---------------------------------------------------------------

app = CSSCrawler

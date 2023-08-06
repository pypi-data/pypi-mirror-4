import nagare.database
from css_crawler.models import URLData
from css_crawler.lib.css import extract
from css_crawler.lib import log


class ColorPalette(object):

    def __init__(self, url_id):
        self.url_id = url_id

    @property
    def _v_url(self):
        return URLData.get(self.url_id)

    def refresh(self):
        url_data = self._v_url

        url, palette = extract.capture_and_extract_colors(
            url_data.url, log)

        url_data.palette = palette
        if url_data.url != url:
            log.warning("Database url %s is different from effective url %s",
                        url_data.url, url)

    def delete(self, comp):
        nagare.database.session.delete(self._v_url)
        comp.answer()

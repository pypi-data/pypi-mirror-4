from nagare import editor
from css_crawler.lib.validator import UrlValidator
from css_crawler.lib.i18n import _


class UrlFetcher(editor.Editor):

    def __init__(self):
        super(UrlFetcher, self).__init__(None)
        self.url = editor.Property('')
        self.url.validate(lambda v: UrlValidator(v, strip=True).not_empty(
            _('cannot be empty')).is_url(_('is not a valid URL')))

    def _commit(self):
        return super(UrlFetcher, self).commit([], ['url'])

    def commit(self, comp):

        if self._commit():
            comp.answer(self.url.value)

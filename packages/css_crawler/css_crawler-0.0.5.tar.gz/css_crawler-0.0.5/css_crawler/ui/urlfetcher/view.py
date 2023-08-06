from component import UrlFetcher

from nagare import presentation
from css_crawler.lib.i18n import _


@presentation.render_for(UrlFetcher)
def render(self, h, comp, *args):

    with h.form:
        with h.div(class_='url-field'):
            h << h.div(h.span('CSS', class_='dark'), h.span('Crawler'),
                       class_='app-name')
            h << h.label(_('URL'), for_='url')
            h << h.input(id='url', name='url', class_='search-field',
                            value=self.url()).action(self.url)
            if self.url.error:
                h << h.div(_('URL'), ' ', self.url.error,
                           class_='error-message')

            h << h.input(type='submit', value=u'\u25bb',
                         class_='submit').action(lambda: self.commit(comp))

    return h.root

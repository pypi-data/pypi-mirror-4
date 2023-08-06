from nagare import presentation

from component import ColorPalette
from css_crawler.lib.i18n import _


@presentation.render_for(ColorPalette)
def render(self, h, comp, *args):
    h << h.a(h.span(_('back to palettes list')),
             title=_('back to palettes list'),
             href=".",
             class_="back-link").action(comp.answer)
    with h.div(class_='result'):
        url_data = self._v_url

        h << h.h1(
            h.a('+', id='toggle@selectors', class_='toggle', href="#"),
            _('Color palette for '),
            h.a(url_data.url, href=url_data.url),
            h.a(h.span(_('refresh')), title=_('refresh'),
                href=url_data.short_url,
                class_='refresh').action(self.refresh),
            h.a(h.span(_('delete')), title=_('delete'),
                href=".",
                class_='delete').action(lambda: self.delete(comp)))

        h << h.br

        palette = url_data.palette

        for k in ['background-color', 'color', 'border-color']:
            v = palette[k]

            h << h.h2(k)

            l = v.items()
            l.sort()

            for (i, (color, rules)) in enumerate(l):

                content = ''
                if k == 'color':
                    content = 'TEXT'

                with h.div(class_='palette-item'):
                    h << h.div(content, class_='color-cell %s' % k,
                               style='%s: %s' % (k, color))
                    h << h.div('color: ', color, ' (', len(rules), ')',
                               class_='color-legend')
                    h << h.a('+', href="#", class_='toggle-selectors collapse')
                    h << h.ul([
                              h.li(r, class_=('selector even' if j % 2 == 0
                                              else 'selector')
                                   ) for j, r in enumerate(set(rules))
                              ], class_='selectors hidden')

                if (i + 1) % 9 == 0:
                    h << h.br
            h << h.br
    h << h.a(h.span(_('back to palettes list')),
             title=_('back to palettes list'),
             href=".",
             class_="back-link").action(comp.answer)
    return h.root

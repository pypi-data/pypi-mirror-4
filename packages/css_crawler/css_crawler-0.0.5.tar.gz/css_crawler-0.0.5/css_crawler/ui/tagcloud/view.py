from component import TagCloud

from nagare import presentation
from css_crawler.lib.i18n import _


@presentation.render_for(TagCloud)
def render(self, h, comp, *args):
    with h.ul(class_='url-list'):

        for (tag, count, scale, (short_url, url_id)) in self.get_tag_cloud():
            with h.li:
                h << h.a(tag,
                         h.span(_("viewed: %d time(s)") % count, h.br,
                                _("permkey: "), short_url, class_='tooltip'),
                         class_="tag%d" % scale, href=short_url).action(
                             lambda url_id=url_id: comp.answer(url_id))

    return h.root

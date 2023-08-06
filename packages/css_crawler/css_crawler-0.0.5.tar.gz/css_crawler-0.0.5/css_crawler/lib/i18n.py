import gettext
from babel.support import Translations, LazyProxy

from nagare.namespaces.xml import _Tag, add_child
import peak.rules

import pkg_resources
import os
import threading

__all__ = ['_', 'ugettext', 'lazy_ugettext', 'N_', 'ungettext',
           'lazy_ungettext']

# loads the catalog -----------------------------------------------------------

package = pkg_resources.Requirement.parse('css_crawler')
dir = pkg_resources.resource_filename(package, os.path.join('data', 'locale'))

_current = threading.local()


def set_lang(lang):
    _current.translations = Translations.load(dir, lang, 'messages')


def _get_translations():
    return getattr(_current, 'translations', gettext.NullTranslations())


def ugettext(msg):
    return _get_translations().ugettext(msg)


_ = ugettext


def lazy_ugettext(msg):
    return LazyProxy(ugettext, msg)


def ungettext(singular, plural, count):
    return _get_translations().ungettext(singular, plural, count)


N_ = ungettext


def lazy_ungettext(singular, plural, count):
    return LazyProxy(ungettext, singular, plural, count)


# Add LazyProxy into render
@peak.rules.when(add_child, (_Tag, LazyProxy))
def add_child(self, s):
    self.add_child(unicode(s))

from nagare import validator
import urlparse
import string


class UrlValidator(validator.StringValidator):

    def is_url(self, msg='Not a valid url'):
        try:
            pieces = urlparse.urlsplit(self.value)

            if pieces.scheme == '':
                self.value = 'http://%s' % self.value

            pieces = urlparse.urlsplit(self.value)

            assert all([pieces.scheme, pieces.netloc])
            assert set(
                pieces.hostname) <= set(string.letters + string.digits + '-.')
            assert pieces.scheme in ['http', 'https']
            return self
        except AssertionError:
            raise ValueError(msg)

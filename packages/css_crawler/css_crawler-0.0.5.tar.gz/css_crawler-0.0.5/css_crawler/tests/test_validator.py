from css_crawler.lib.validator import UrlValidator
import unittest


class ValidatorTestCase(unittest.TestCase):

    def test_port(self):
        """
        Capture a page with no stylesheet
        """
        url = "http://localhost:8080/path/"
        validator = UrlValidator(url)

        self.assertEqual(validator.is_url().value, url)

    def test_no_port(self):
        """
        Capture a page with no stylesheet
        """
        url = "http://localhost/path/"
        validator = UrlValidator(url)

        self.assertEqual(validator.is_url().value, url)

    def test_basicauth(self):
        """
        Capture a page with no stylesheet
        """
        url = "http://user:password@localhost/path/"
        validator = UrlValidator(url)

        self.assertEqual(validator.is_url().value, url)

    def test_noscheme(self):
        """
        Capture a page with no stylesheet
        """
        url = "localhost/path/"
        validator = UrlValidator(url)

        self.assertEqual(validator.is_url().value, 'http://' + url)

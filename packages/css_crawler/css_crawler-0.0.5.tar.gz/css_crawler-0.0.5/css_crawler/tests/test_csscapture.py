import helpers
from css_crawler.lib.css.capture import CSSCapture
import unittest


class CSSCaptureTestCase(unittest.TestCase):

    def test_no_stylesheet(self):
        """
        Capture a page with no stylesheet
        """
        url = "NO_URL"
        capture = CSSCapture(fetcher=helpers.no_stylesheet_fetcher)
        res = capture.capture(url)
        self.assertEqual(res, (None, []))

    def test_stylesheet(self):
        """
        Capture a page with a test stylesheet
        """
        url = "NO_URL"
        capture = CSSCapture(fetcher=helpers.base_stylesheet_fetcher)
        url, res = capture.capture(url)
        self.assertEqual(len(res), 1)

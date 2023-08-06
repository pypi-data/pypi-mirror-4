import cssutils
import os
import helpers
import unittest


class CSSExtractTestCase(unittest.TestCase):

    def test_simple(self):
        """
        Test if extract_colors can get all colors from simple stylesheet
        """
        stylesheet = helpers.load_stylesheet_file(
            'css_crawler/tests/data/stylesheets/simple.css')

        res = helpers.extract_color_from_stylesheets([stylesheet])

        self.assertEqual(res, {
            'color': {'#000000': [u'root']},
            'border-color': {'#888888': [u'root']},
            'background-color': {'#ffffff': [u'root']}})

    def test_import(self):
        """Test if extract_colors can get all colors from simple stylesheet
        import
        """
        stylesheet = helpers.load_stylesheet_file(
            'css_crawler/tests/data/stylesheets/import_simple.css')
        stylesheet = cssutils.resolveImports(stylesheet)

        res = helpers.extract_color_from_stylesheets([stylesheet])

        self.assertEqual(res, {
            'color': {'#000000': [u'root']},
            'border-color': {'#888888': [u'root']},
            'background-color': {'#ffffff': [u'root']}})

    def test_variables(self):
        """Test if extract_colors can get all colors from stylesheet with
        variables define in a @variables rule
        """
        stylesheet = helpers.load_stylesheet_file(
            'css_crawler/tests/data/stylesheets/variables.css')

        res = helpers.extract_color_from_stylesheets([stylesheet])

        self.assertEqual(res, {
            'color': {'#000000': [u'root']},
            'border-color': {'#888888': [u'root']},
            'background-color': {'#ffffff': [u'root']}})

    def test_fromstring(self):
        """
        Test if extract_colors can get all colors from stylesheet string
        """
        css = """
        root {
            color: #000000;
            background-color: #ffffff;
            border-color: #888888;
        }
        """

        stylesheet = helpers.load_stylesheet_string(css)

        res = helpers.extract_color_from_stylesheets([stylesheet])

        self.assertEqual(res, {
            'color': {'#000000': [u'root']},
            'border-color': {'#888888': [u'root']},
            'background-color': {'#ffffff': [u'root']}})

    def test_fromstring_import(self):
        """
        Test if extract_colors can get all colors from stylesheet string with
        import
        """
        css = """
        @import url("simple.css");
        """

        # compute stylesheet dir path as a valid url
        href = cssutils.helper.path2url(
            os.path.join(os.path.dirname(__file__), 'data', 'stylesheets'))
        stylesheet = helpers.load_stylesheet_string(css, href + '/')

        res = helpers.extract_color_from_stylesheets([stylesheet])

        self.assertEqual(res, {
            'color': {'#000000': [u'root']},
            'border-color': {'#888888': [u'root']},
            'background-color': {'#ffffff': [u'root']}})

    def test_fromstring_variables_import(self):
        """
        Test if extract_colors can get all colors from stylesheet string with
        import and variables
        """
        css = """
        @import url("variables.css");
        """

        # compute stylesheet dir path as a valid url
        href = cssutils.helper.path2url(
            os.path.join(os.path.dirname(__file__), 'data', 'stylesheets'))
        stylesheet = helpers.load_stylesheet_string(css, href + '/')

        res = helpers.extract_color_from_stylesheets([stylesheet])

        self.assertEqual(res, {
            'color': {'#000000': [u'root']},
            'border-color': {'#888888': [u'root']},
            'background-color': {'#ffffff': [u'root']}})

    def test_nng(self):
        """
        Test if extract_colors can get all colors from stylesheet of
        net-ng site
        """
        stylesheets = [
            helpers.load_stylesheet_file(
                'css_crawler/tests/data/stylesheets/netng/reset.css'),
            helpers.load_stylesheet_file(
                'css_crawler/tests/data/stylesheets/netng/screen.css')
        ]

        res = helpers.extract_color_from_stylesheets(stylesheets)

        self.assertEqual(res, {
            'color': {
                '#6fafe0': [u'blockquote'],
                '#554c43': [u'.black'],
                '#443b32': [u'#contents', u'#left h1'],
                '#999999': [u'.small'],
                '#0c89e7': [u'a', u'h1', u'h3', u'blockquote .signature',
                            u'.atouts', u'#footer h4'],
                '#ffffff': [u'#mainmenu li.selected',
                u'#mainmenu li.selected a',
                            u'#footer'],
                '#767676': [u'.news', u'.news h2']},
            'border-color': {
                '#000000': [u'.wishes'],
                '#144971': [u'#footer'],
                '#bbbbbb': [u'.news h2', u'.news img', u'.reflist a .vignette',
                            u'.reflist img']},
            'background-color': {
                '#03263f': [u'body'],
                '#063354': [u'.bluebg'],
                '#ffffff': [u'.news .yeartab', u'.news .year', u'.main'],
                '#eaeaea': [u'#contents'], '#001a2c': [u'#footer']}})

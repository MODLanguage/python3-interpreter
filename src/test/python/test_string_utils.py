import unittest

from string_utils import EscapeStrings


class TestStringUtilsCase(unittest.TestCase):
    def test_escaper(self):
        """A few random checks"""
        escaper = EscapeStrings()
        self.assertEqual('"', escaper.unescape('~"'))
        self.assertEqual('"', escaper.unescape('\\"'))
        self.assertEqual('=', escaper.unescape('~='))
        self.assertEqual('=', escaper.unescape('\\='))
        self.assertEqual(':', escaper.unescape('\\:'))
        self.assertEqual(':', escaper.unescape('~:'))


if __name__ == '__main__':
    unittest.main()

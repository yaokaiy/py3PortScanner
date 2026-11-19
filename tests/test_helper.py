import unittest

from pyportscanner.etc.helper import get_domain


class HelperTest(unittest.TestCase):
    def test_get_domain(self):
        for target, expected in (
            ("https://docs.python.org/3/library/unittest.mock.html", "docs.python.org"),
            (" HTTPS://LOCALHOST:8000/check ", "localhost"),
            ("127.0.0.1", "127.0.0.1"),
            ("localhost:8000", "localhost"),
            ("//localhost:8000/check", "localhost"),
        ):
            with self.subTest(target=target):
                self.assertEqual(get_domain(target), expected)

    def test_invalid_target(self):
        for target in (
            "", "https://", "https://[::1", "ftp://localhost", "invalid host",
            "localhost\0.example", "localhost:bogus", "localhost:65536", None,
        ):
            with self.subTest(target=target):
                self.assertEqual(get_domain(target), "")

import unittest
from html.parser import HTMLParser
from pathlib import Path


class OptionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        if tag == "option":
            self.values.append(dict(attrs).get("value"))


class MarkupTests(unittest.TestCase):
    def test_all_engine_and_language_options_are_real_elements(self):
        parser = OptionParser()
        parser.feed((Path(__file__).resolve().parent.parent / "web" / "index.html").read_text(encoding="utf-8"))
        for value in ["offline", "muse", "en", "ta", "ml", "kn", "hi"]:
            self.assertIn(value, parser.values)

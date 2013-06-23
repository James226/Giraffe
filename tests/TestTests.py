import random
import unittest
import cStringIO
from template import *

class TestTemplate(unittest.TestCase):

    def setUp(self):
        self.indexPage = template()

    def test_WriteHeaderShouldAddBasicHeaderImplementation(self):
        output = cStringIO.StringIO()
        self.indexPage._writeHeader(output)
        header = output.getvalue()
        output.close()
        self.assertRegexpMatches(header, "import cStringIO")
        self.assertRegexpMatches(header, "def __init__")
        self.assertRegexpMatches(header, "def OutputPage")
        self.assertRegexpMatches(header, "self.buffer = ")

    def test_WriteFooterShouldCloseOutputBuffer(self):
        output = cStringIO.StringIO()
        self.indexPage._writeFooter(output)
        header = output.getvalue()
        output.close()
        self.assertRegexpMatches(header, "self.buffer.close()")

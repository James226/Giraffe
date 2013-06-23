import random
import unittest
import cStringIO
import os
import time
import random
from template import *

class TestTemplate(unittest.TestCase):

    def setUp(self):
        self.indexPage = template()
        name = 'test_' + str(random.randint(10000, 20000))
        self.cachePath = self.indexPage.GetCachePath(name)
        self.templatePath = self.indexPage.GetTemplatePath(name)

    def tearDown(self):
        if os.path.exists(self.cachePath):
            os.remove(self.cachePath)

        if os.path.exists(self.cachePath + 'c'):
            os.remove(self.cachePath + 'c')

        if os.path.exists(self.templatePath):
            os.remove(self.templatePath)

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

    def test_GetCachePathShouldReturnRelativePathToCacheFile(self):
        self.assertEqual('cache/test.py', self.indexPage.GetCachePath('test'))

    def test_GetTemplatePathShouldReturnRelativePathToTemplateFile(self):
        self.assertEqual('templates/test.thtml', self.indexPage.GetTemplatePath('test'))

    def test_ShouldRecachePageShouldReturnTrueIfCacheFileMissing(self):
        with open(self.templatePath, 'w') as templateFile:
            time.sleep(0.1)

        self.assertTrue(self.indexPage._shouldRecachePage(self.templatePath, self.cachePath))


    def test_ShouldRecachePageShouldReturnTrueIfCacheOlderThanTemplate(self):
        with open(self.templatePath, 'w') as templateFile:
            time.sleep(0.1)
            with open(self.cachePath, 'w') as cacheFile:
                time.sleep(0.1)

        self.assertTrue(self.indexPage._shouldRecachePage(self.cachePath, self.templatePath))

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

        if not os.path.exists('cache/'):
            os.mkdir('cache')

        if not os.path.exists('templates/'):
            os.mkdir('templates')

    def tearDown(self):
        if os.path.exists(self.cachePath):
            os.remove(self.cachePath)

        if os.path.exists(self.cachePath + 'c'):
            os.remove(self.cachePath + 'c')

        if os.path.exists(self.templatePath):
            os.remove(self.templatePath)

    def test_WriteHeaderShouldAddBasicHeaderImplementation(self):
        output = cStringIO.StringIO()
        self.indexPage._writeHeader(output, "test")
        header = output.getvalue()
        output.close()
        self.assertRegexpMatches(header, "import cache\.Page")
        self.assertRegexpMatches(header, "class test\(cache\.Page\.Page\):")
        self.assertRegexpMatches(header, "def __init__")
        self.assertRegexpMatches(header, "super\(test, self\)\.__init__\(\)")
        self.assertRegexpMatches(header, "def OutputPage")

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

        self.assertTrue(self.indexPage._shouldCachePage(self.templatePath, self.cachePath))

    def test_ShouldRecachePageShouldReturnTrueIfCacheOlderThanTemplate(self):
        with open(self.templatePath, 'w') as templateFile:
            time.sleep(0.1)
            with open(self.cachePath, 'w') as cacheFile:
                time.sleep(0.1)

        self.assertTrue(self.indexPage._shouldCachePage(self.cachePath, self.templatePath))

    def test_WriteLineShouldReplaceVariables(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '{Test}')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header, "\t\tif 'Test' in self.Nests['']:\n\t\t\tself.buffer.write(self.Nests['']['Test'])\n")

    def test_WriteLineShouldReplaceIfBlocks(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- IF Var -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header, "\t\tif self.Nests['']['Var']:\n")

    def test_WriteLineShouldReplaceElseBlocks(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- ELSE -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header, "\telse:\n")

    def test_WriteLineShouldReplaceEndIfBlocks(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- ENDIF -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header, "\n")

    def test_WriteLineShouldWriteContentBeforeVariables(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, 'Testing{Variable}')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header, "\t\tself.buffer.write('''Testing''')\n" +
                                         "\t\tif 'Variable' in self.Nests['']:\n" +
                                         "\t\t\tself.buffer.write(self.Nests['']['Variable'])\n")

    def test_WriteLineShouldWriteContentAfterVariables(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '{Variable}Testing')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header, "\t\tif 'Variable' in self.Nests['']:\n" +
                                         "\t\t\tself.buffer.write(self.Nests['']['Variable'])\n" +
                                         "\t\tself.buffer.write('''Testing''')\n")

    def test_WriteLineShouldWriteContentBetweenVariables(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, 'TextBefore{Variable}TextAfter')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header,
                         "\t\tself.buffer.write('''TextBefore''')\n" +
                         "\t\tif 'Variable' in self.Nests['']:\n" +
                         "\t\t\tself.buffer.write(self.Nests['']['Variable'])\n" +
                         "\t\tself.buffer.write('''TextAfter''')\n")

    def test_WriteLineShouldAddExtraIndentForNestedIf(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- IF Test -->\nIs True:<!-- IF Value -->Unreachable Code<!-- ENDIF -->\n<!-- ENDIF -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header,
                         "\t\tif self.Nests['']['Test']:\n"
                         "\t\t\tself.buffer.write('''\nIs True:''')\n" +
                         "\t\t\tif self.Nests['']['Value']:\n"
                         "\t\t\t\tself.buffer.write('''Unreachable Code''')\n\n" +
                         "\t\t\tself.buffer.write('''\n''')\n\n")

    def test_WriteLineShouldReplaceBeginAndEndStatements(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- BEGIN TestNest -->Data<!-- END TestNest -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header,
                         "\t\tif 'TestNest' in self.Nests:\n"
                         "\t\t\tfor TestNest in self.Nests['TestNest']:\n" +
                         "\t\t\t\tself.buffer.write('''Data''')\n\n")

    def test_WriteLineShouldReplaceNestedBeginAndEndStatements(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- BEGIN TestNest --><!-- BEGIN NestedNest -->Data<!-- END NestedNest --><!-- END TestNest -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header,
                         "\t\tif 'TestNest' in self.Nests:\n" +
                         "\t\t\tfor TestNest in self.Nests['TestNest']:\n" +
                         "\t\t\t\tif 'NestedNest' in TestNest:\n"
                         "\t\t\t\t\tfor TestNest_NestedNest in TestNest['NestedNest']:\n"
                         "\t\t\t\t\t\tself.buffer.write('''Data''')\n\n\n")

    def test_WriteLineShouldReplaceVariablesWithinNests(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- BEGIN TestNest -->{TestNest.Variable}<!-- END TestNest -->')
        header = output.getvalue()
        output.close()
        self.assertSequenceEqual(header,
                         "\t\tif 'TestNest' in self.Nests:\n" +
                         "\t\t\tfor TestNest in self.Nests['TestNest']:\n" +
                         "\t\t\t\tif 'Variable' in TestNest:\n" +
                         "\t\t\t\t\tself.buffer.write(TestNest['Variable'])\n\n")

    def test_WriteLineShouldReplaceVariablesWithinNestedNests(self):
        output = cStringIO.StringIO()
        self.indexPage._writeLine(output, '<!-- BEGIN TestNest --><!-- BEGIN NestedNest -->{NestedNest.Variable}<!-- END NestedNest --><!-- END TestNest -->')
        header = output.getvalue()
        output.close()
        self.maxDiff = None
        self.assertSequenceEqual(header,
                         "\t\tif 'TestNest' in self.Nests:\n" +
                         "\t\t\tfor TestNest in self.Nests['TestNest']:\n" +
                         "\t\t\t\tif 'NestedNest' in TestNest:\n"
                         "\t\t\t\t\tfor TestNest_NestedNest in TestNest['NestedNest']:\n"
                         "\t\t\t\t\t\tif 'Variable' in TestNest_NestedNest:\n" +
                         "\t\t\t\t\t\t\tself.buffer.write(TestNest_NestedNest['Variable'])\n\n\n")
import imp
import re
import os.path

class template:
    def __init__(self):
            pass

    @classmethod
    def Load(cls, name):
        template = cls()
        cls.cachePath = cls.GetCachePath(name)
        cls.templatePath = cls.GetTemplatePath(name)
        if template._shouldRecachePage(cls.templatePath, cls.cachePath):
            template.CachePage(name)
        cachedFile = imp.load_source(name, cls.cachePath)
        template.page = getattr(cachedFile, name)()
        return template

    def GetCachePath(self, name):
        return 'cache/%s.py' % name

    def GetTemplatePath(self, name):
        return 'templates/%s.thtml' % name

    def _shouldRecachePage(self, templateName, cacheName):
        return (not os.path.exists(cacheName)) or (os.path.getmtime(templateName)) > (os.path.getmtime(cacheName))

    def CachePage(self, name):
        print("Caching file %s" % (name))
        with open(self.cachePath, 'w') as cache_file:
            self._writeHeader(cache_file, name)
            with open(self.templatePath, 'r') as template_file:
                content = template_file.readline()
                while content != '':
                    self._writeLine(cache_file, content)
                    content = template_file.read()

            self._writeFooter(cache_file)

    def _writeHeader(self, stream, name):
        stream.write("import cStringIO\n\n")
        stream.write("class %s:\n\n\t" % name)
        stream.write("def __init__(self):\n\t\tself.buffer = cStringIO.StringIO()\n\n")
        stream.write("\tdef OutputPage(self):\n\t\tself.buffer.write('''")

    def _writeFooter(self, stream):
        stream.write("''')\n\n")
        stream.write("\t\toutput = self.buffer.getvalue()\n")
        stream.write("\t\tself.buffer.close()\n")
        stream.write("\t\treturn output\n\n")

    def _writeLine(self, stream, content):
        content = re.sub("{([a-zA-Z0-9_-]+)}", "''')\n\t\tself.buffer.write(self.\\1)\n\t\tself.buffer.write('''", content)
        content = re.sub("<!-- IF ([a-zA-Z0-9\s=\!]+) -->", "''')\n\t\tif \\1:\n\t\t\tself.buffer.write('''", content)
        content = re.sub("<!-- ELSE -->", "''')\n\t\telse:\n\t\t\tself.buffer.write('''", content)
        content = re.sub("<!-- ENDIF -->", "''')\n\t\tself.buffer.write('''", content)
        stream.write(content)

    def SetVariable(self, name, value):
        setattr(self.page, name, value)

    def OutputPage(self):
        return self.page.OutputPage()


import imp
import re
import os.path

class template:
    def __init__(self):
            pass

    @classmethod
    def Load(cls, name):
        template = cls()
        cls.cachePath = template.GetCachePath(name)
        cls.templatePath = template.GetTemplatePath(name)
        if template._shouldRecachePage(template.templatePath, template.cachePath):
            template.CachePage(name)
        cachedFile = imp.load_source(name, template.cachePath)
        template.page = getattr(cachedFile, name)()
        return template

    def GetCachePath(self, name):
        return 'cache/%s.py' % name

    def GetTemplatePath(self, name):
        return 'templates/%s.thtml' % name

    def _shouldRecachePage(self, templateName, cacheName):
        return (not os.path.exists(cacheName)) or (os.path.getmtime(templateName)) > (os.path.getmtime(cacheName))

    def CachePage(self, name):
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
        stream.write("\tdef OutputPage(self):\n")

    def _writeFooter(self, stream):
        stream.write("\n\n")
        stream.write("\t\toutput = self.buffer.getvalue()\n")
        stream.write("\t\tself.buffer.close()\n")
        stream.write("\t\treturn output\n\n")

    def _writeLine(self, stream, content):
        currentPosition = 0
        replacementMatches = re.finditer("{([a-zA-Z0-9_-]+)}|<!-- (IF|ELSE|ENDIF)(\s([a-zA-Z0-9\s=!]+))? -->", content)
        for match in replacementMatches:
            if match.start() - currentPosition > 0:
                self._processHTML(stream, content[currentPosition:match.start()])

            if match.group(1) is not None:
                self._processVariable(stream, match)
            else:
                self._processStatement(stream, match)

            currentPosition = match.end()
        self._processHTML(stream, content[currentPosition:])

    def _processHTML(self, stream, content):
        stream.write("\t\tself.buffer.write('''")
        stream.write(content)
        stream.write("''')\n")

    def _processVariable(self, stream, match):
        stream.write("\t\tself.buffer.write(self." + match.group(1) + ")\n")
        pass

    def _processStatement(self, stream, match):
        if match.group(2) == "IF":
            stream.write("\t\tif " + match.group(4) + ":\n\t")
        elif match.group(2) == "ELSE":
            stream.write("\t\telse:\n\t")
        elif match.group(2) == "ENDIF":
            stream.write("\n")
        pass

    def SetVariable(self, name, value):
        setattr(self.page, name, value)

    def OutputPage(self):
        return self.page.OutputPage()


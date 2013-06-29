import imp
import re
import os.path


class template:
    def __init__(self):
        self.currentTab = 2
        self.page = None
        self.currentNest = []

    @classmethod
    def Load(cls, name):
        template = cls()
        cls.cachePath = template.GetCachePath(name)
        cls.templatePath = template.GetTemplatePath(name)
        if template._shouldCachePage(template.templatePath, template.cachePath):
            template.CachePage(name)
        cachedFile = imp.load_source(name, template.cachePath)
        template.page = getattr(cachedFile, name)()
        return template

    def GetCachePath(self, name):
        return 'cache/%s.py' % name

    def GetTemplatePath(self, name):
        return 'templates/%s.thtml' % name

    def _shouldCachePage(self, templateName, cacheName):
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
        stream.write("import cache.Page\n\n")
        stream.write("class %s(cache.Page.Page):\n\n\t" % name)
        stream.write("def __init__(self):\n")
        stream.write("\t\tsuper(%s, self).__init__()\n\n" % name)
        stream.write("\tdef OutputPage(self):\n")

    def _writeFooter(self, stream):
        stream.write("\n\n")
        stream.write("\t\toutput = self.buffer.getvalue()\n")
        stream.write("\t\tself.buffer.close()\n")
        stream.write("\t\treturn output\n\n")

    def _writeLine(self, stream, content):
        currentPosition = 0
        replacementMatches = re.finditer("{(([A-Za-z0-9]+)\.)?([a-zA-Z0-9_-]+)}|<!-- (IF|ELSE|ENDIF|BEGIN|END)(\s([a-zA-Z0-9\.]+))? -->",
                                         content)
        for match in replacementMatches:
            if match.start() - currentPosition > 0:
                self._processHTML(stream, content[currentPosition:match.start()])

            if match.group(3) is not None:
                self._processVariable(stream, match)
            else:
                self._processStatement(stream, match)

            currentPosition = match.end()
        if len(content) > currentPosition:
            self._processHTML(stream, content[currentPosition:])

    def _processHTML(self, stream, content):
        stream.write(self._getTabs() + "self.buffer.write('''")
        stream.write(content)
        stream.write("''')\n")

    def _processVariable(self, stream, match):
        if match.group(1) is not None:
            index = self.currentNest.index(match.group(2))
            if index is not None:
                nestVariable = '_'.join(self.currentNest[:index+1])
                stream.write(self._getTabs() + "if '" + match.group(3) + "' in " + nestVariable + ":\n")
                self._incrementTab()
                stream.write(self._getTabs() + "self.buffer.write(" + nestVariable + "['" + match.group(3) + "'])\n")
                self._decrementTab()
            else:
                stream.write("self.buffer.write('''" + match.group(0) + "'''")
        else:
            stream.write(self._getTabs() + "if '" + match.group(3) + "' in self.Nests['']:\n")
            self._incrementTab()
            stream.write(self._getTabs() + "self.buffer.write(self.Nests['']['" + match.group(3) + "'])\n")
            self._decrementTab()

    def _processStatement(self, stream, match):
        if match.group(4) == "IF":
            if '.' not in match.group(6):
                stream.write(self._getTabs() + "if '" + match.group(6) + "' in self.Nests[''] and self.Nests['']['" + match.group(6) + "']:\n")
                self._incrementTab()
            else:
                variableParts = match.group(6).split('.')
                index = self.currentNest.index(variableParts[0])
                if index is not None:
                    nestVariable = '_'.join(self.currentNest[:index+1])
                    stream.write(self._getTabs() + "if '" + variableParts[1] + "' in " + nestVariable + " and " + nestVariable + "['" + variableParts[1] + "']:\n")
                    self._incrementTab()
        elif match.group(4) == "ELSE":
            self._decrementTab()
            stream.write(self._getTabs() + "else:\n")
            self._incrementTab()
        elif match.group(4) == "ENDIF":
            stream.write("\n")
            self._decrementTab()
        elif match.group(4) == "BEGIN":
            if len(self.currentNest) == 0:
                stream.write(self._getTabs() + "if '" + match.group(6) + "' in self.Nests:\n")
                self._incrementTab()
                stream.write(self._getTabs() + "for " + match.group(6) + " in self.Nests['" + match.group(6) + "']:\n")
            else:
                parentNest = '_'.join(self.currentNest)
                stream.write(self._getTabs() + "if '" + match.group(6) + "' in " + parentNest + ":\n")
                self._incrementTab()
                stream.write(self._getTabs() + "for " + parentNest + '_' + match.group(6) + " in " + parentNest + "['" + match.group(6) + "']:\n")
            self.currentNest.append(match.group(6))
            self._incrementTab()
        elif match.group(4) == "END":
            if len(self.currentNest) > 0 and self.currentNest.pop() == match.group(6):
                stream.write("\n")
                self._decrementTab()
                self._decrementTab()
            else:
                print("Invalid template syntax. Attempted to end nest %s. Current Nest Structure: %s",
                      match.group(6),
                      '.'.join(self.currentNest))

    def _getTabs(self):
        return '\t' * self.currentTab

    def _incrementTab(self):
        self.currentTab += 1

    def _decrementTab(self):
        self.currentTab -= 1

    def SetVariable(self, name, value):
        self.page.Nests[''][name] = value

    def AddNest(self, nestName, variables):
        self.AddSubNest(self.page.Nests, nestName, variables)
        return variables

    def AddSubNest(self, parentNest, nestName, variables):
        if not nestName in parentNest:
            parentNest[nestName] = []

        parentNest[nestName].append(variables)
        return variables

    def OutputPage(self):
        return self.page.OutputPage()


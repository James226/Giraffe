import imp
import re
import os.path

class template:
        def GetCachePath(self, name):
                return 'cache/%s.py' % (name)

        def GetTemplatePath(self, name):
                return 'templates/%s.thtml' % (name)
        
        def __init__(self):
                pass

        @classmethod
	def Load(cls, name):
                template = cls()
		if template._shouldRecachePage('templates/index.thtml', 'cache/index.py'):
			template.CachePage("index")
		file = imp.load_source("index", 'cache/index.py')
		template.page = getattr(file, "index")()
		return template

	def _shouldRecachePage(self, templateName, cacheName):
                return (not os.path.exists(cacheName)) or (os.path.getmtime(templateName)) > (os.path.getmtime(cacheName))
		
	def CachePage(self, filename):
		print("Caching file %s" % (filename))
		with open('cache/index.py', 'w') as cache_file:
			self._writeHeader(cache_file)
			with open('templates/index.thtml', 'r') as template_file:
				content = template_file.readline()
				while content != '':
					self._writeBlock(cache_file, content)
					content = template_file.read()
			
			self._writeFooter(cache_file)
				
	def _writeHeader(self, stream):
                stream.write("import cStringIO\n\n")
                stream.write("class index:\n\n\t")
                stream.write("def __init__(self):\n\t\tself.buffer = cStringIO.StringIO()\n\n")
                stream.write("\tdef OutputPage(self):\n\t\tself.buffer.write('''")

        def _writeFooter(self, stream):
                stream.write("''')\n\n")
		stream.write("\t\toutput = self.buffer.getvalue()\n")
		stream.write("\t\tself.buffer.close()\n")
		stream.write("\t\treturn output\n\n")

	def _writeBlock(self, stream, content):
                content = re.sub("{([a-zA-Z0-9_-]+)}", "''')\n\t\tself.buffer.write(self.\\1)\n\t\tself.buffer.write('''", content)
                content = re.sub("<!-- IF ([a-zA-Z0-9\s=\!]+) -->", "''')\n\t\tif \\1:\n\t\t\tself.buffer.write('''", content)
                content = re.sub("<!-- ELSE -->", "''')\n\t\telse:\n\t\t\tself.buffer.write('''", content)
                content = re.sub("<!-- ENDIF -->", "''')\n\t\tself.buffer.write('''", content)
		stream.write(content)
	
	def SetVariable(self, name, value):
		setattr(self.page, name, value)
		
	def OutputPage(self):
		return self.page.OutputPage()
	

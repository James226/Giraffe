import imp
import re
import os.path

class template:

	def __init__(self, name):
		if (not os.path.exists("cache/index.py")) or (os.path.getmtime("templates/index.thtml")) > (os.path.getmtime("cache/index.py")):
			self.CachePage("index")
		file = imp.load_source("index", "cache/index.py")
		self.page = file.index()
		self.page.test = "Test"
		
	def CachePage(self, filename):
		print("Caching file %s" % (filename))
		with open('cache/index.py', 'w') as cache_file:
			cache_file.write("class index:\n\n\tdef OutputPage(self):\n\t\treturn '''")
			with open('templates/index.thtml', 'r') as template_file:
				content = template_file.read()
				while content != '':
					content = re.sub("{([a-zA-Z0-9_-]+)}", "''' + self.\\1 + '''", content)
					cache_file.write(content)
					content = template_file.read()
			
			cache_file.write("'''")
				
			
	
	def SetVariable(self, name, value):
		setattr(self.page, name, value)
		
	def OutputPage(self):
		return self.page.OutputPage()
	
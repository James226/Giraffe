import imp
import cherrypy
from template import *


class WebServer:
    def index(self):
        indexPage = template.Load("index")
        indexPage.SetVariable("Test", "Test!!!")
        test = indexPage.AddNest("Nest", {
            'NestTitle': 'Test Nest'
        })
        indexPage.AddSubNest(test, "NestedNest", {'NestContent': 'Nested Nest!'})
        indexPage.AddNest("Nest", {})
        return indexPage.OutputPage()


    # Expose the index method through the web. CherryPy will never
    # publish methods that don't have the exposed attribute set to True.
    index.exposed = True


import os.path

settings = os.path.join(os.path.dirname(__file__), 'settings.conf')

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.quickstart(WebServer(), config=settings)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(WebServer(), config=settings)

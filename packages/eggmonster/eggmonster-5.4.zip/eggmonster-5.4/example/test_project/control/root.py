from . import startup
from eggmonster import env
import os

import cherrypy

from fab.cp_tools import FabDispatcher
from .hello import HelloPage

mapper = FabDispatcher()

# Layout your URL scheme here
mapper.add_route('hello', '', HelloPage())

# Cherrypy configuration here
app_conf = {'/' : {'request.dispatch' : mapper}}

def start():
    cherrypy.config.update({
            'server.socket_port' : env.port,
    })
    cherrypy.quickstart(None, '/', config=app_conf)

if __name__ == "__main__":
    start()

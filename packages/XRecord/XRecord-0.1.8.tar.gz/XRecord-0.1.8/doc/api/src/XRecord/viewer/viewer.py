#!/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import path

try:
    from werkzeug import Request, Response, SharedDataMiddleware, ClosingIterator
    from werkzeug.routing import Map, Rule
    from werkzeug.exceptions import HTTPException
    from werkzeug.debug import DebuggedApplication
    
    from mako.lookup import TemplateLookup
except ImportError:
    print """
XRecord Viewer application requires the werkzeug WSGI module, and the mako template engine.
It seems there was a problem importing them. Make sure you have them installed in your PYTHONPATH.
They may be added installed via easy_install:
easy_install -U Werkzeug
easy_install -U mako
"""
    sys.exit(1)

from utils import local, local_manager, url_map 
import handlers

root_path = path.abspath(path.dirname(__file__))
template_lookup = TemplateLookup(directories=[path.join(root_path, 'templates')], input_encoding='utf-8')


class DatabaseViewer(object):
    def __init__(self, connectfn):
        local.application = self
        self.connectfn = connectfn
        
    def __call__(self, environ, start_response):
        local.application = self
        local.db = self.connectfn()
        
        request = Request ( environ )
        local.url_adapter = adapter = url_map.bind_to_environ(request.environ)

        try:
            endpoint, values = adapter.match()

            handler = getattr(handlers, endpoint)

            response = Response(mimetype='text/html')
            response_data = handler(request, response, **values)
            
            template = template_lookup.get_template(endpoint + '.html')
            response.data = template.render_unicode( db = local.db, data = response_data, url_for = lambda e, **v : adapter.build(e, v), url_values=values )            
        except HTTPException, e:
            response = e

        return ClosingIterator (response(environ, start_response), [local_manager.cleanup] )

def make_app (db_factory, debugger=False):
    application = SharedDataMiddleware ( DatabaseViewer(db_factory), {
        '/static' : path.join(root_path, 'templates/static')
        })
    if debugger:
        application = DebuggedApplication (application, evalex=True)
    return application

def run(db_factory, address="0.0.0.0", port=3000):
    from werkzeug import run_simple
    application = SharedDataMiddleware ( DatabaseViewer(db_factory), {
        '/static' : path.join(root_path, 'templates/static')
        })
    application = DebuggedApplication (application, evalex=True)
    run_simple ( address, port, application )



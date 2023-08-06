from werkzeug import Request, Response, SharedDataMiddleware, Local, LocalManager
from werkzeug.routing import Map, Rule

local = Local()
local_manager = LocalManager([local])

url_map = Map()

def expose(rule, **kw):
    def _decorator(fn):
        kw['endpoint'] = fn.__name__
        url_map.add ( Rule(rule, **kw) )
        return fn
    return _decorator

def url_for(endpoint, _external=False, **values):
    return local.url_adapter.build (endpoint, values, force_external=_external)

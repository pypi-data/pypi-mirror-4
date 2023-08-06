from XRecord import connection_factory, viewer

#Example WSGI script

f = connection_factory ( "sqlite", name="/home/coobs/web/xrecord/test.db")
application = viewer.make_app (f, True)
__author__="Kuba"
__date__ ="$2009-11-05 22:54:10$"

from version import version


__all__ = [ "db", "mysql", "sqlite", "viewer", "ordereddict" ]

def connect( backend, **kwargs):
    if backend.lower() == "mysql":
        from mysql import XRecordMySQL
        return XRecordMySQL ( **kwargs )
    elif backend.lower() == "postgresql":
        from postgresql import XRecordPostgreSQL
        return XRecordPostgreSQL ( **kwargs )
    elif backend.lower() == "sqlite":
        from sqlite import XRecordSqlite
        return XRecordSqlite ( **kwargs )
    else:
        raise NotImplementedError ( 'Unknown database backend type: `{0}`'.format(backend.lower()) )

def connection_factory (backend, **kwargs):
    from functools import partial
    return partial(connect, backend, **kwargs)

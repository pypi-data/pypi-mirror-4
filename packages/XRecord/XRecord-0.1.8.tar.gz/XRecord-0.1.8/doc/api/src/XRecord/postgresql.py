# -*- coding: utf-8 -*-
from contextlib import contextmanager
import datetime
import re
from db import XRecordDatabase
import information_schema

__all__ = [ "XRecordPostgreSQL" ]

try:
    import pg, pgdb
    apilevel = pgdb.apilevel
    threadsafety = pgdb.threadsafety
    paramstyle = pgdb.paramstyle
    connect = pgdb.connect
except ImportError:
    from sys import stderr
    print >>stderr, "Unable to import the pg module. Please check if this extension is installed within your PYTHONPATH."
    
    
class XRecordPostgreSQL(XRecordDatabase):
    Backend = "POSTGRESQL"

    class ResultWrapper:
        def __init__(self, result):
            self.pgresult = result
            self._results = None
            self.current = 0

        def __len__(self): return self.pgresult.ntuples()

        def next():
            try:
                return self.results[self.current]
            except IndexError:
                return None
            finally:
                self.current += 1

        def describe(self):
            return self.fields
        
        @property
        def fields(self):
            return self.pgresult.listfields()
        
        @property
        def results(self):
            if self._results is None:
                self._results = self.pgresult.getresult()
            return self._results

        def __getitem__(self, idx):
            return self.results[idx]

        def __iter__(self):
            return iter(self.results)
        
    def __init__(self, **kwargs):
        XRecordDatabase.__init__(self, **kwargs)

        
        self._host = kwargs.get ( 'host', self.connection_defaults.get ('host', None) )
        self._port = kwargs.get ( 'port', self.connection_defaults.get ('port', 5432) )
        self._dbname = kwargs.get ( 'name', self.connection_defaults.get ('name') )
        self._user = kwargs.get ( 'user', self.connection_defaults.get ('user') ) 
        self._pass = kwargs.get ( 'password', self.connection_defaults.get ('password', '') ) 

        #self._info = information_schema.PostgreSQLInformationSchema (self)
        self._affected_rows = 0
        self._insert_id = None
        self.Reconnect()

        self._dbapi = None

    def cursor(self):
        return self.dbapi.cursor()
    def close(self):
        return self.dbapi.close()
    
    @property
    def dbapi(self):
        if not self._dbapi: self._dbapi = pgdb.connect (
            host = self._host, user = self._user,
            passwd = self._pass, dbname = self._dbname, port = self._port )
        return self._dbapi        
        
    @property
    def InformationSchema(self):
        if not hasattr(self, "_info"):
            self._info = information_schema.PostgreSQLInformationSchema(self)
        return self._info

    def Escape(self, v):
        return pg.escape_string(str(v))
    
    def Reconnect(self):
        try:
            self._conn.close()
        except AttributeError:
            pass
        except pg.Error:
            pass
        
        self._conn = pg.connect ( host = self._host, user = self._user,
                                      passwd = self._pass, dbname = self._dbname, port = self._port )        
        return self
    
    def Test(self):
        try:
            self._conn.query ( "SELECT 1+1" )
        except pg.Error:
            return False
        
        return True

    @classmethod
    def ErrorTranslation(self, orig):
        import _mysql_exceptions as my
        try:
            raise orig
        except pg.OperationalError, e:
            return self.OperationalError (e)
        except pg.Warning, e:
            return self.Warning (e)
        except pg.InterfaceError, e:
            return self.InterfaceError (e)
        except pg.DatabaseError, e:
            return self.DatabaseError (e)
        except pg.DataError, e:
            return self.DataError (e)
        except pg.OperationalError, e:
            return self.OperationalError (e)
        except pg.IntegrityError, e:
            return self.IntegrityError (e)
        except pg.InternalError, e:
            return self.InternalError (e)
        except pg.ProgrammingError, e:
            return self.ProgrammingError (e)        

        return self.Error(orig)

    def DoSQL(self, sql, *args):
        str_args = map(lambda x : "'{0}'".format ( self.Escape(x) ), args )
        sql = sql % tuple(str_args)        
        result = self.ResultWrapper( self._conn.query ( sql ) )
        return result                

    def Close(self):        
        try:
            self._conn.close()
        except pg.Error:
            pass        
        
    def AffectedRows(self, result = None):
        return self._affected_rows

    def InsertId(self, result):
        return self._insert_id
    
    def FetchResultValue (self, result, row, col):
        if len(result) > row:
            row_data = result[row]
        else:
            return None

        if len(row_data) > 0:
            return row_data[col]
        
        return None
    
    def FetchRow(self, result, row):
        if len(result) > row:
            return result[row]
        return None

    def FetchRows(self, result):
        return iter(result)

    def FetchNextRow(self, result):
        return result.next()

    
    def FetchNextRowObject(self, result, **kwargs):
        return self._RowToObject (result.fields, self.FetchNextRow(result), **kwargs )

    def FetchNextRowAssoc(self, result, **kwargs):
        return self._RowToAssoc (result.fields, self.FetchNextRow(result), **kwargs )

    def _RowToObject ( self, description, row_data, **kwargs):
        if "__ucase_attr" in kwargs:
            c_filter_fn = str.upper
        elif "__lcase_attr" in kwargs:
            c_filter_fn = str.lower
        else:
            c_filter_fn = lambda x:x

        if row_data is None: return None
        obj = self.Record()
        for (idx, column_value) in enumerate(row_data):            
            cname, value = c_filter_fn(description[idx]), column_value
            setattr (obj, cname, value)
        return obj
    
    def _RowToAssoc ( self, description, row_data, **kwargs):
        if "__ucase_attr" in kwargs:
            c_filter_fn = str.upper
        elif "__lcase_attr" in kwargs:
            c_filter_fn = str.lower
        else:
            c_filter_fn = lambda x:x

        if row_data is None: return None
        obj = {}
        for (idx, column_value) in enumerate(row_data):
            cname, value = c_filter_fn(description[idx]), column_value
            obj[cname] = value            
        return obj

    def FetchRowObject(self, result, row, **kwargs):
        return self._RowToObject(result.describe(), self.FetchRow(result, row), **kwargs)    
    
    def FetchRowAssoc(self, result, row, **kwargs):
        return self._RowToAssoc(result.describe(), self.FetchRow(result, row), **kwargs)    
    
    def FetchResultsObject(self, result, **kwargs):        
        return [ self._RowToObject ( result.describe(), row, **kwargs) for row in self.FetchRows(result) ]
        
    def FetchResultsAssoc(self, result, **kwargs):
        return [ self._RowToAssoc ( result.describe(), row, **kwargs) for row in self.FetchRows(result) ]

        

    

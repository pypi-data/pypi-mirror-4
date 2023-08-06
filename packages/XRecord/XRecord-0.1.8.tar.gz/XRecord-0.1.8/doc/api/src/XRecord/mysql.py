# -*- coding: utf-8 -*-
from contextlib import contextmanager
import datetime
import re
from db import XRecordDatabase
import information_schema

__all__ = [ "XRecordMySQL" ]

try:
    import _mysql
    import MySQLdb
    apilevel = MySQLdb.apilevel
    threadsafety = MySQLdb.threadsafety
    paramstyle = MySQLdb.paramstyle
    connect = MySQLdb.connect
except ImportError:
    from sys import stderr
    print >>stderr, "Unable to import the MySQLdb module. Please check if this extension is installed within your PYTHONPATH."


class XRecordMySQL(XRecordDatabase):
    Backend = "MYSQL"
    
    def __init__(self, **kwargs):
        XRecordDatabase.__init__(self, **kwargs)
        from MySQLdb.constants import FIELD_TYPE as FT
        from MySQLdb.converters import conversions
        from functools import partial
        
        self._host = kwargs.get ( 'host', self.connection_defaults.get ('host', 'localhost') )
        self._port = kwargs.get ( 'port', self.connection_defaults.get ('port', 3306) )
        self._dbname = kwargs.get ( 'name', self.connection_defaults.get ('name') )
        self._user = kwargs.get ( 'user', self.connection_defaults.get ('user') ) 
        self._pass = kwargs.get ( 'password', self.connection_defaults.get ('password', '') ) 
        self._charset = kwargs.get ( 'charset', self.connection_defaults.get ('charset', 'utf8') ) 

        #self._info = information_schema.MySQLInformationSchema (self)
        
        self.escape_function = _mysql.escape_string        
        self._conversion = conversions
        
        s_decode = lambda s: s.decode ( self._charset )
        self._conversion[FT.VARCHAR] = s_decode
        self._conversion[FT.VAR_STRING] = s_decode
        self._conversion[FT.STRING] = s_decode
        self._conversion[FT.BLOB] = s_decode
        self._conversion[FT.MEDIUM_BLOB] = s_decode
        self._conversion[FT.LONG_BLOB] = s_decode
        self._conversion[FT.TINY_BLOB] = s_decode

        #print "VARCHAR", FT.VARCHAR
        self.Reconnect()

    #DBAPI interface
    def cursor(self): return self._conn.cursor()
    def close(self): return self._conn.close()
    
    
    @property
    def InformationSchema(self):
        if not hasattr(self, "_info"):
            self._info = information_schema.MySQLInformationSchema(self)
        return self._info

    def Escape(self, v):
        return self.escape_function(str(v))
    
    def Reconnect(self):
        from _mysql_exceptions import ProgrammingError
        try:
            self._conn.close()
        except AttributeError:
            pass
        except ProgrammingError:
            pass
        
        self._conn = _mysql.connect ( host = self._host, user = self._user,
                                      passwd = self._pass, db = self._dbname, port = self._port )
        self._conn.set_character_set ( self._charset )
        self._conn.query ( "SET CHARACTER SET '{0}'".format(self._charset) )
        self._conn.query ("SET sql_mode='ANSI_QUOTES';")
        self._conn.select_db ( self._dbname )
        return self
    
    def Test(self):
        import _mysql_exceptions 
        try:
            self._conn.ping()
        except _mysql_exceptions.Error:
            return False        
        except _mysql_exceptions.InterfaceError:
            return False
            
        return True

    @classmethod
    def ErrorTranslation(self, orig):
        import _mysql_exceptions as my
        try:
            raise orig
        except my.OperationalError, e:
            return self.OperationalError (e)
        except my.Warning, e:
            return self.Warning (e)
        except my.InterfaceError, e:
            return self.InterfaceError (e)
        except my.DatabaseError, e:
            return self.DatabaseError (e)
        except my.DataError, e:
            return self.DataError (e)
        except my.OperationalError, e:
            return self.OperationalError (e)
        except my.IntegrityError, e:
            return self.IntegrityError (e)
        except my.InternalError, e:
            return self.InternalError (e)
        except my.ProgrammingError, e:
            return self.ProgrammingError (e)        

        return self.Error(orig)

    def DoSQL(self, sql, *args):
        str_args = map(lambda x : "'{0}'".format ( self.Escape(x) ), args )
        sql = sql % tuple(str_args)
        self._conn.query ( sql )
        return self._conn.store_result()                

    def Close(self):        
        from _mysql_exceptions import ProgrammingError
        try:
            self._conn.close()
        except ProgrammingError:
            pass        
        
    def AffectedRows(self, result = None):
        return self._conn.affected_rows()

    def InsertId(self, result):
        return self._conn.insert_id()
    
    def FetchResultValue (self, result, row, col):
        if result.num_rows() > row:
            result.data_seek (row)
        else:
            return None
        row_data = result.fetch_row()
        if len(row_data) > 0:
            if result.num_fields() > 0:
                return row_data[0][col]
        return None
    
    def FetchRow(self, result, row):
        if result.num_rows() > row:
            result.data_seek (row)
            return result.fetch_row()[0]
        return None

    def FetchRows(self, result):            
        while True:            
            row = self.FetchNextRow(result)
            if row:
                yield row
            else:
                raise StopIteration

    def FetchNextRow(self, result):
        try:
            return result.fetch_row()[0]
        except IndexError:
            return None
    
    def FetchNextRowObject(self, result, **kwargs):
        return self._RowToObject (result.describe(), self.FetchNextRow(result), **kwargs )

    def FetchNextRowAssoc(self, result, **kwargs):
        return self._RowToAssoc (result.describe(), self.FetchNextRow(result), **kwargs )

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
            cname, value = self._ParseValue (description[idx], column_value)
            setattr (obj, c_filter_fn(cname), value)
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
            cname, value = self._ParseValue (description[idx], column_value)            
            obj[c_filter_fn(cname)] = value            
        return obj

    def _ParseValue(self, description, value):        
        cname, ctype, cmax, clength, _, cdec, cnull = description                
        
        if value is None: return cname, value
        conv = self._conversion[ctype] 
        if isinstance(conv, list):
            _, conv = conv[0]
        
        return cname, conv(value)
    
    
    def FetchRowObject(self, result, row, **kwargs):
        return self._RowToObject(result.describe(), self.FetchRow(result, row), **kwargs)    
    
    def FetchRowAssoc(self, result, row, **kwargs):
        return self._RowToAssoc(result.describe(), self.FetchRow(result, row), **kwargs)    
    
    def FetchResultsObject(self, result, **kwargs):                
        return [ self._RowToObject ( result.describe(), row, **kwargs) for row in self.FetchRows(result) ]
        
    def FetchResultsAssoc(self, result, **kwargs):
        return [ self._RowToAssoc ( result.describe(), row, **kwargs) for row in self.FetchRows(result) ]

        

    

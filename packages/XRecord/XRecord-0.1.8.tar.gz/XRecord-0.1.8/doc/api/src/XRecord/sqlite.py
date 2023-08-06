# -*- coding: utf-8 -*-
from contextlib import contextmanager
import datetime
import re
from db import XRecordDatabase, Record

from information_schema import SqliteInformationSchema

__all__ = ["XRecordSqlite"]

try:
    import sqlite3
    apilevel = sqlite3.apilevel
    threadsafety = sqlite3.threadsafety
    paramstyle = sqlite3.paramstyle
    connect = sqlite3.connect
except ImportError:
    from sys import stderr
    print >>stderr, "Unable to import the Sqlite3 module. Please check if this extension is installed within your PYTHONPATH:"
    print >>stderr, "\n".join(sys.path)

class XRecordSqlite(XRecordDatabase):
    Backend = "SQLITE"

    class ResultWrapper:
        def __init__ (self, cursor):
            self.close = cursor.close
            self.next = cursor.next
            self.description = cursor.description
            self.lastrowid = cursor.lastrowid
            self._data = None
            self.cursor = cursor

        @property
        def data(self):
            if self._data is None:
                self._data = self.cursor.fetchall()
            return self._data
        
        @property
        def rowcount(self):
             return len(self.data)

        def __getitem__(self, key):
            return self.data[key]

        
    def __init__(self, **kwargs):
        XRecordDatabase.__init__(self, **kwargs)        
        self._dbname = kwargs.get ( 'name', self.connection_defaults.get ('name') )
        self._info = self.InformationSchema
        self.Reconnect()

    def cursor(self): return self._conn.cursor()
    def close(self): return self._conn.close()
    
    @property
    def InformationSchema(self):
        if not hasattr(self, "_info"):
            self._info = SqliteInformationSchema(self)
        return self. _info

    def Reconnect(self):
        try:
            self._conn.close()
        except AttributeError:
            pass
        
        self._conn = sqlite3.connect ( self._dbname )
        self._conn.row_factory = sqlite3.Row
        self._conn.isolation_level = None
        return self

    @classmethod
    def ErrorTranslation(self, orig):
        try:
            raise orig
        except sqlite3.OperationalError, e:
            return self.OperationalError (e)
        except sqlite3.Warning, e:
            return self.Warning (e)
        except sqlite3.InterfaceError, e:
            return self.InterfaceError (e)
        except sqlite3.DatabaseError, e:
            return self.DatabaseError (e)
        except sqlite3.DataError, e:
            return self.DataError (e)
        except sqlite3.OperationalError, e:
            return self.OperationalError (e)
        except sqlite3.IntegrityError, e:
            return self.IntegrityError (e)
        except sqlite3.InternalError, e:
            return self.InternalError (e)
        except sqlite3.ProgrammingError, e:
            return self.ProgrammingError (e)        

        return self.Error(orig)
    
    def Test(self):
        try:
            c = self._conn.cursor()
        except:
            return False
        return True

    def BuildDeleteSQL(self, table, limit=1, **where):
        where_clause = " AND ".join ( map (lambda x: "{0} = '{1}'".format (x[0], x[1]), where.items()) )
        return "DELETE FROM {0} WHERE {1}".format ( table, where_clause, limit )
            
    def BuildSelectSQL(self, table, limit, *select, **where):
        where_clause = " AND ".join ( map (lambda x: "{0} = '{1}'".format (x[0], x[1]), where.items()) )
        return "SELECT {0} FROM {1} WHERE {2} LIMIT {3}".format ( ",".join(select), table, where_clause,  limit )
    
    def BuildInsertSQL(self, table, **kwargs):
        columns = ",".join(kwargs.keys())
        values = ",".join (map(lambda x: "{0}".format(x), kwargs.values()))
        return "INSERT INTO {0} ({1}) VALUES ({2})".format (table, columns, values)

    def BuildUpdateSQL(self, table, where, limit=1, **values):
        updates = ",".join ( map( lambda x: "{0} = {1}".format(x[0], x[1]), values.items()) )
        where = " AND ".join ( map( lambda x: "{0} = '{1}'".format(x[0], x[1]), where.items()) )
        return "UPDATE {0} SET {1} WHERE {2}".format (table, updates, where, limit)
    
    def DoSQL(self, sql, *args):
        c = self._conn.cursor()
        c.execute ( sql, args )
        return self.ResultWrapper(c)

    def CleanupSQL(self, result):
        result.close()
    
    def Close(self):        
        self._conn.close()
        
    def AffectedRows(self, result = None):
        return 0
    
    def InsertId(self, result):
        return result.lastrowid
    
    def FetchResultValue (self, result, row, col):
        if result.rowcount > row:
            row_data = result[row]
        else:
            return None
        if len(result.description) > col:
            return row_data[col]
        return None
    
    def FetchRow(self, result, row):
        if result.rowcount > row:
             return result[row]
        return None

    def FetchRows(self, result):            
        while True:
            yield self.FetchNextRow(result)

    def FetchNextRow(self, result):
        return result.next()

    def _RowToObject ( self, description, row_data, **kwargs):
        if "__ucase_attr" in kwargs:
            c_filter_fn = str.upper
        elif "__lcase_attr" in kwargs:
            c_filter_fn = str.lower
        else:
            c_filter_fn = lambda x:x
            
        if row_data is None: return None
        obj = self.Record()
        for (column_name, column_value) in zip(map(lambda x: x[0], description),row_data):            
            setattr (obj, c_filter_fn(column_name), column_value)
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
        for (column_name, column_value) in zip(map(lambda x: x[0], description),row_data):            
            obj[c_filter_fn(column_name)] = column_value
        return obj


    def FetchRowObject(self, result, row, **kwargs):
        return self._RowToObject(result.description, self.FetchRow(result, row), **kwargs)    
    
    def FetchNextRowObject(self, result, **kwargs):        
        return self._RowToObject(result.description, self.FetchNextRow(result), **kwargs)    

    def FetchNextRowAssoc(self, result, **kwargs):        
        return self._RowToAssoc(result.description, self.FetchNextRow(result), **kwargs)    
    
    def FetchRowAssoc(self, result, row, **kwargs):
        return self._RowToAssoc(result.description, self.FetchRow(result, row), **kwargs)    
    
    def FetchResultsObject(self, result, **kwargs):                
        return [ self._RowToObject ( result.description, row, **kwargs) for row in self.FetchRows(result) ]
        
    def FetchResultsAssoc(self, result, **kwargs):
        return [ self._RowToAssoc ( result.description, row, **kwargs) for row in self.FetchRows(result) ]

        

    

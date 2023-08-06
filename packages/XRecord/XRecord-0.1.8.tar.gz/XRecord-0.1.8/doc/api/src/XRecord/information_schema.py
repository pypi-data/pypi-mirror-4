# -*- coding: utf-8 -*-
from ordereddict import OrderedDict

class InformationSchema:

    def __init__(self, db):
        self.DB = db
        self._primary_keys = None
        self._foreign_keys = None
        self._tables = None
        self._table_constraints = None
        self.table_info = {}
        
    @property
    def PrimaryKeys(self):
        if self._primary_keys is None:
            self._primary_keys = {}
            pks = self.DB.ArrayObjectIndexedList (
                """
                SELECT C.TABLE_NAME, K.COLUMN_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS C INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE K
                ON C.CONSTRAINT_NAME = K.CONSTRAINT_NAME AND C.TABLE_SCHEMA = K.TABLE_SCHEMA AND K.TABLE_NAME = C.TABLE_NAME
                WHERE
                C.TABLE_SCHEMA = '{0}' AND C.CONSTRAINT_TYPE = 'PRIMARY KEY'
                """.format (self.DB._dbname), "TABLE_NAME", __ucase_attr=1 )
            for (t, pk) in pks.items():
                self._primary_keys [t] = tuple(map ( lambda x: x.COLUMN_NAME, pk ))
        return self._primary_keys

    @property
    def ForeignKeys(self):
        if self._foreign_keys is None:
            fks = self.DB.ArrayObjectIndexedList (
                """
                SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS C INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE K
                ON C.CONSTRAINT_NAME = K.CONSTRAINT_NAME AND C.TABLE_SCHEMA = K.TABLE_SCHEMA AND K.TABLE_NAME = C.TABLE_NAME
                WHERE C.TABLE_SCHEMA = '{0}' AND C.CONSTRAINT_TYPE = 'FOREIGN KEY'                
                """.format (self.DB._dbname), "TABLE_NAME", __ucase_attr=1 )
            self._foreign_keys = fks
            
        return self._foreign_keys

    @property
    def Tables(self):
        if self._tables is None:
            self._tables = self.DB.ArrayObjectIndexed (
                """
                SELECT * FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{0._dbname}'
                """.format (self.DB), "TABLE_NAME", __ucase_attr=1
                )
        return self._tables

    @property
    def TableConstraints(self):
        if self._table_constraints is None:
            self._table_constraints = self.DB.ArrayObjectIndexedList (
                """
                SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = '{0._dbname}'
                """.format (self.DB), "TABLE_NAME", __ucase_attr=1
                )
        return self._table_constraints
    
    def GetColumnsForTable(self, table):
        return self.DB.ArrayObjectIndexed (
            """
            SELECT * FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{0._dbname}' AND TABLE_NAME = '{1}' ORDER BY ORDINAL_POSITION
            """.format(self.DB,table), "COLUMN_NAME", __ucase_attr=1)

    def GetTableInfo(self, table):
        return self.Tables[table]
        
    def GetTableConstraints(self, table):
        return self.TableConstraints.get(table, [])

    def GetTableChildren(self, table):
        children = []
        for fk_all in self.ForeignKeys.values():
            for fk in fk_all:
                if fk.REFERENCED_TABLE_NAME == table:
                    children.append (fk)
        return children
        

    def SerializeToFile(self, file):
        import pickle
        for table in self.Tables:
            self.GetForTable (table)

        data = {
            'PK' : self.PrimaryKeys,
            'FK' : self.ForeignKeys,
            'CONSTRAINTS' : self.TableConstraints,
            'TABLES' : self.table_info
            }
        
        pickle.dump ( data, file )

    def UnserializeFromFile(self, file):
        import pickle

        data = pickle.load ( file )

        self._primary_keys = data['PK']
        self._foreign_keys = data['FK']
        self._table_constraints = data['CONSTRAINTS']
        self.table_info = data['TABLES']

        return data
    
    def GetForTable(self, table):
        if table not in self.table_info:

            table_info = self.GetTableInfo(table)
            columns = self.GetColumnsForTable (table)
                
            #All table constraints - primary, foreign and unique keys
            constraints = self.GetTableConstraints(table)
            #Children - other tables' foreign keys pointing to this table
            children = self.GetTableChildren(table)

            primary_key = None
            foreign_keys = {}
            unique = []

            for c in constraints:
                 key_columns = self.DB.ArrayObject (
                     """
                     SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                     WHERE CONSTRAINT_NAME = '{0.CONSTRAINT_NAME}' AND TABLE_NAME = '{1}'
                     """.format(c,table), __ucase_attr=1)
                 if c.CONSTRAINT_TYPE == "UNIQUE":
                     unique.append ( key_columns )

            try:
                for fk in self.ForeignKeys[table]:
                    foreign_keys[fk.COLUMN_NAME] = fk
            except KeyError:
                pass

            try:
                primary_key = self.PrimaryKeys[table]
            except KeyError:
                primary_key = ()
                
            #Many-to-many relationships detection, through tables that:
            # 1. Have a foreign key to this table (f1)
            # 2. Have a foreign key to one other table (f2)
            # 3. Have (f1,f2) or (f2,f1) as their primary key

            #We already have f1 (children):
            mtm = {}
            for f1 in children:
                #Get other Foreign Keys (from cache)
                f2 = self.ForeignKeys[f1.TABLE_NAME]
                for f2x in f2:
                    if f2x.CONSTRAINT_NAME == f1.CONSTRAINT_NAME: continue
                    #For each foreign key, other than the one pointing to this table, check if primary key matches:
                    if (f1.COLUMN_NAME, f2x.COLUMN_NAME) == self.PrimaryKeys[f1.TABLE_NAME] or (f2x.COLUMN_NAME, f1.COLUMN_NAME) == self.PrimaryKeys[f1.TABLE_NAME]:
                        mtm[f1.TABLE_NAME] = {
                            'to' : f2x.REFERENCED_TABLE_NAME,
                            'via' : f1.TABLE_NAME,
                            'via_to_column' : f2x.COLUMN_NAME,
                            'to_column' : f2x.REFERENCED_COLUMN_NAME,                        
                            'via_my_column' : f1.COLUMN_NAME,
                            'my_column' : f1.REFERENCED_COLUMN_NAME
                            }

            self.table_info[table] = {
                'table' : table_info,
                'columns' : columns,
                'primary_key' : primary_key,
                'foreign_keys' : foreign_keys,
                'unique' : unique,
                'children' : children,
                'mtm' : mtm
                }
          
        return self.table_info[table]

class MySQLInformationSchema(InformationSchema):
    pass

class PostgreSQLInformationSchema(InformationSchema):

    def GetColumnsForTable(self, table):
        return self.DB.ArrayObjectIndexed (
            """
            SELECT * FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_CATALOG = '{0._dbname}' AND TABLE_NAME = '{1}' ORDER BY ORDINAL_POSITION
            """.format(self.DB,table), "COLUMN_NAME", __ucase_attr=1)

    @property
    def ForeignKeys(self):
        if self._foreign_keys is None:
            fks = self.DB.ArrayObjectIndexedList (
                """
                select ordinal_position, t.constraint_catalog as constraint_schema, t.constraint_type, t.constraint_name,
                       t.table_name, k.column_name, u.table_name as REFERENCED_TABLE_NAME, u.column_name as REFERENCED_COLUMN_NAME,
                       u.table_catalog as REFERENCED_TABLE_SCHEMA
                       from information_schema.table_constraints t inner join information_schema.constraint_column_usage u on u.constraint_name = t.constraint_name
                       inner join information_schema.key_column_usage k on k.constraint_name = t.constraint_name
                       where t.table_catalog='{0}' and t.constraint_type = 'FOREIGN KEY' and u.table_catalog = '{0}'
                """.format (self.DB._dbname), "TABLE_NAME", __ucase_attr=1 )
            self._foreign_keys = fks
            
        return self._foreign_keys
    
    @property
    def PrimaryKeys(self):
        if self._primary_keys is None:
            self._primary_keys = {}
            pks = self.DB.ArrayObjectIndexedList (
                """
                select t.table_name, u.column_name from information_schema.table_constraints t
                inner join information_schema.constraint_column_usage u on u.constraint_name = t.constraint_name
                where t.table_catalog='{0}' and t.constraint_type = 'PRIMARY KEY' and u.table_catalog = '{0}'
                """.format (self.DB._dbname), "TABLE_NAME", __ucase_attr=1 )
            for (t, pk) in pks.items():
                self._primary_keys [t] = tuple(map ( lambda x: x.COLUMN_NAME, pk ))
        return self._primary_keys

    
class SqliteInformationSchema:

    def __init__(self, db):
        self.DB = db
        self._meta_data_ = None

    def SerializeToFile(self, file):
        pass

    def UnserializeFromFile(self, file):
        pass
        
    def Prefetch(self):
        tables = self.DB.ArrayAssocIndexed ( "SELECT * FROM sqlite_master WHERE type='table'", "name" )
        for tbl in tables:
            tables[tbl]['children'] = []
            tables[tbl]['mtm'] = []

        for tbl in tables:
            tables[tbl]['columns'] = self.DB.ArrayObjectIndexed ( "PRAGMA table_info ({0})".format (tbl), "name" )
            tables[tbl]['fk'] = self.DB.ArrayObjectIndexed ( "PRAGMA foreign_key_list ({0})".format (tbl), "from" )
            tables[tbl]['pk'] = tuple(map( lambda x: x.name, filter ( lambda x: x.pk == 1, tables[tbl]['columns'].values() )))
            for fk in tables[tbl]['fk'].values():
               tables[fk.table]['children'].append ( fk )

        translated = {}
        for tbl in tables:
            translated_tbl = {}
            tinfo = self.DB.Record()
            tinfo['TABLE_SCHEMA'] = self.DB._dbname
            tinfo['TABLE_NAME'] = tbl
            tinfo['TABLE_TYPE'] = "BASE TABLE"
            tinfo['AUTO_INCREMENT'] = "autoincrement" in tables[tbl]['sql']
            translated_tbl['info'] = tinfo
            translated_tbl['columns'] = {}
            for op, (column, c) in enumerate(tables[tbl]['columns'].items()):
                t_column = self.DB.Record()
                t_column['ORDINAL_POSITION'] = op
                t_column['TABLE_SCHEMA'] = self.DB._dbname
                t_column['TABLE_NAME'] = tbl
                t_column['COLUMN_NAME'] = column
                t_column['COLUMN_TYPE'] = c.type
                t_column['DATA_TYPE'] = c.type
                t_column['COLUMN_DEFAULT'] = c.dflt_value
                translated_tbl['columns'][column] = t_column
            translated_tbl['fk'] = {}
            for op, (column, fk) in enumerate(tables[tbl]['fk'].items()):
                t_fk = self.DB.Record()
                t_fk['ORDINAL_POSITION'] = op
                t_fk['CONSTRAINT_SCHEMA'] = self.DB._dbname
                t_fk['CONSTRAINT_NAME'] = self.DB._dbname + '_' + tbl + '_' + column + '_' + fk.table + '_' + hex(id(fk))
                t_fk['TABLE_NAME'] = tbl
                t_fk['TABLE_SCHEMA'] = self.DB._dbname
                t_fk['CONSTRAINT_TYPE'] = "FOREIGN KEY"
                t_fk['COLUMN_NAME'] = column
                t_fk['REFERENCED_TABLE_SCHEMA'] = self.DB._dbname
                t_fk['REFERENCED_TABLE_NAME'] = fk.table
                t_fk['REFERENCED_COLUMN_NAME'] = fk.to
                translated_tbl['fk'][column] = t_fk
            translated_tbl['children'] = []
            translated_tbl['mtm'] = {}
            translated_tbl['pk'] = tables[tbl]['pk']
            translated[tbl] = translated_tbl

        for tbl, t in translated.items():
            for (column, fk) in t['fk'].items():
                translated[fk.REFERENCED_TABLE_NAME]['children'].append (fk)

        for tbl, t in translated.items():
            for f1 in t['children']:
                f2 = translated[f1.TABLE_NAME]['fk']
                pk2 = translated[f1.TABLE_NAME]['pk']
                for fk_column, f2x in f2.items():
                    if f2x.CONSTRAINT_NAME == f1.CONSTRAINT_NAME: continue
                    if (f1.COLUMN_NAME, f2x.COLUMN_NAME) == pk2 or (f2x.COLUMN_NAME, f1.COLUMN_NAME) == pk2:
                        t['mtm'][f1.TABLE_NAME] = {
                            'to' : f2x.REFERENCED_TABLE_NAME,
                            'via' : f1.TABLE_NAME,
                            'via_to_column' : f2x.COLUMN_NAME,
                            'to_column' : f2x.REFERENCED_COLUMN_NAME,                        
                            'via_my_column' : f1.COLUMN_NAME,
                            'my_column' : f1.REFERENCED_COLUMN_NAME
                            }                
                    pass
                pass
            pass
        self._meta_data_ = translated

    @property
    def Tables(self):
        if self._meta_data_ is None:
            self.Prefetch()
        return self._meta_data_
    
    def GetForTable(self, table):
        if self._meta_data_ is None:
            self.Prefetch()
        md = self._meta_data_[table]
        return  { 'table' : md['info'],
                  'columns' : md['columns'],
                  'primary_key' : md['pk'],
                  'foreign_keys' : md['fk'],
                  'unique' : [],
                  'children' : md['children'],
                  'mtm' : md['mtm'] }



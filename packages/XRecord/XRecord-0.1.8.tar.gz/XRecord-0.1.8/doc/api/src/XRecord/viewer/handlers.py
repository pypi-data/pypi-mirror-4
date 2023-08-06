from utils import expose, local

@expose('/')
def index(request, response):
    pass

@expose('/tables/')
def tables(request, response):
    tables = [t for t in local.db.Tables]
    tables.sort()
    
    return [local.db.XSchema(i) for i in tables]

@expose('/table/<tablename>')
def table(request, response, tablename):
    return local.db.XSchema (tablename)

@expose('/data/<tablename>')
def data(request, response, tablename):
    ret = local.db.Record()
    try:
        ret.schema = local.db.XSchema(tablename)
    except KeyError:
        ret.schema = None
        ret.records = []
    else:
        ret.records = local.db.XArray (tablename, 'SELECT * FROM "{0}" LIMIT 25'.format (tablename) )

    return ret
                                      

    

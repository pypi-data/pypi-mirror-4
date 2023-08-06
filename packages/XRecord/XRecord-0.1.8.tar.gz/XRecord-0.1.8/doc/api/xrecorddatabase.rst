Managing database connections
=============================

.. automodule:: xRecord

The basic :class:`XRecordDatabase` functionality is not very different from other `connection` objects provided by
RDBMS backend drivers. It connects to the backend, and serves as a proxy for sending queries and receiving results.

It also provides an API to query the database and receive results in object format 
(:class:`Record` and :class:`XRecord`), but some backend drivers also have this functionality built-in.

The main difference comes from the way XRecord ORM was utilized, before it was called `XRecord ORM` - it was used
in long-running daemons and system services. All of these are vulnerable to database backend failures, restarts, 
network downtime etc., so graceful re-connection had to be made easy at the `database API` level. It's nothing fancy, 
but it does its job, a primitive example could look like this ::
    
    while True:
        try:
	   arr = db.XArray("blog_entry")
   	   for e in arr:
	      do_something()
        except db.Error:
	   while not db.Test():
	      time.sleep(10)
	      db.Reconnect()
    	 
XRecord was also used in short-lived programs, some of which required speed, and the additional overhead caused
by fetching meta-data for each session was simply not acceptable. This is why we decided for the meta-data
fetching functions to be `lazy`, ie. fetching it only when it is needed (when XRecords for a specific table are
instantiated), so when not using the `XRecord.X?????` functions, no hidden hits to the database are made.


XRecordDatabase
---------------

.. autoclass:: XRecordDatabase

   .. automethod:: getInstance
   .. automethod:: Test
   .. automethod:: Close
   .. automethod:: Reconnect
   .. automethod:: CheckConnection
   
   .. autoattribute:: Connection
   .. attribute:: Manager
   
      The ``Manager`` attribute provides a way to access the generated
      classes for database tables. This may come in handy if you defined
      custom class methods for your table proxy.::

         >> db.Manager.blog_entry.getByCategory ( "programming", "python" )
	 [<xrecord::blog_entry(1)>, <xrecord::blog_entry(2)>]
      	            

   .. automethod:: SQLLog

   .. automethod:: CommandQuery
   .. automethod:: InsertQuery   

   .. automethod:: SingleValue
   .. automethod:: SingleObject
   .. automethod:: ArrayObject
   .. automethod:: ArrayObjectIndexed
   .. automethod:: ArrayObjectIndexedList

   .. automethod:: SingleAssoc
   .. automethod:: ArrayAssoc
   .. automethod:: ArrayAssocIndexed
   .. automethod:: ArrayAssocIndexedList

   .. automethod:: XRecord
   .. automethod:: XSingle
   .. automethod:: XArray
   .. automethod:: XArrayIndexed
   .. automethod:: XArrayIndexedList
   
   .. automethod:: XRecordRefCacheEnable
   .. automethod:: XRecordRefCacheDisable

   .. automethod:: Initialize
      
XRecordMySQL
------------
.. class:: XRecordMySQL
   
    The named attributes accepted by the constructor of this class are:
    
    name
	database name

    host
	server host name

    port
	server tcp port

    user
	user name

    password
	user's password
   


XRecordSqlite
-------------

.. class:: XRecordSqlite
   
    The named attributes accepted by the constructor of this class are:
    
    name
	path to the file containing the database

XRecordPostgreSQL
-----------------

.. class:: XRecordPostgreSQL
   
    The named attributes accepted by the constructor of this class are:
    
    name
	database name

    host
	server host name

    port
	server tcp port

    user
	user name

    password
	user's password



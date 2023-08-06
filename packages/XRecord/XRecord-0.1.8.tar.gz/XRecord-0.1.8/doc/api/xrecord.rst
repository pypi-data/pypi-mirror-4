Working with records / data rows
================================

Working with relational databases, in majority of applications, comes down to working with
*rows of data*, also known as *records*. Therefore, for a library used in the database-abstraction
layer   , whether it wants to be called an ORM or not, it is most important to make using these records
as comfortable as possible.
   
The most commonly used standard for such libraries is DBAPI (currently v2.0). It's working, it's complete, 
optimized and it has a well designed, widely accepted interfaces. The problem is, that to run a database 
task using DBAPI, you usually have to:

    #. Create a cursor
    #. Execute the query
    #. Iterate over the cursor
    #. Extract data from the cursor for each row
    #. Run a seperate query to, for eg. update related data.
    #. Close the cursor

This becomes tedious in larger applications, which start to look like majority of their code is 
related to data fetching / saving.

ORMs on the other hand provide a simpler mechanism:
   	
    #. Execute the query
    #. Use/modify the returned objects

What is hidden from you is the fact that for each row you want to work with, the ORM has to instantiate
a class, and fill its attributes - something you'd have to do one way or another.

XRecord provides you with two alternative ways to run database queries. The first - using basic record objects,
is more suited for running complex SQL queries and working with the results. The functions used for this method, are
the documented methods of XRecordDatabase, that have *Object* in their name. The objects they return have no reference
to the database, table or row they came from, cannot be saved, updated or deleted without writing additional SQL. They
also do not follow intra-table relationships. In fact, the only difference between them and the return values from
DBAPI queries is possibility of accessing values via object attributes, and that there is no need to create and use
a cursor object.

The second way XRecord lets you access data is the reason why we call it an ORM. The functions using this method are
the ones with names starting with 'X'. These functions return instances of classes derived from the :class:`XRecord` 
class. 
Each such instance represents a row of data in a specified table, and can easily fetch referenced rows, child rows
and rows related via many-to-many relationships. You may update, delete and insert rows without writing a single
line of SQL.

The :class:`XRecord` subclasses for each table are generated on-the-fly from the metadata in your RDBMS. 
It means you have to specify all the primary and foreign keys in your DDL scripts. More about this can be found in 
the :doc:`xschema` section.

The :class:`XRecord` subclasses may be further extended to provide a richer object interface to your data.

.. automodule:: xRecord

Basic record objects - Record
-----------------------------

.. autoclass:: Record
 

Active record objects - XRecord
-------------------------------
      

.. autoclass:: XRecord
   
   .. automethod:: fetch
   .. automethod:: reload
   .. automethod:: save
   .. automethod:: insert
   .. automethod:: delete
   .. automethod:: nullify
   .. automethod:: serialized
   
   .. autoattribute:: PK
   .. autoattribute:: Table
   .. autoattribute:: SCHEMA   


Extending XRecord
-----------------

   When XRecord subclasses are generated from meta-data, they provide a set of basic functions for working
   with records of a specified table (described above). It is also possible to further subclass them to
   extend data row objects with custom functionality. An example::
   	  
	  @db.CustomXRecord("blog_entry")
	  class blog_articles:
	  	def __repr__(self):
		    return "Entry: '" + self.title + "'"
		
		def last_comments(self, number=10):
		    return self.DB.XArray ("comment", 
                        "SELECT c.* FROM comment WHERE entry=? ORDER BY when DESC LIMIT ?",
			(self.id, number) )
		
		@classmethod
		def last_entries(cls, number=10):
		    return self.DB.XArray ( "blog_entry", 
		        "SELECT * FROM blog_entry ORDER BY when DESC LIMIT ?",
			(number, ) )

   What we've done here is we customized the ``blog_articles`` class, so that each subsequent instance will
   have a custom string representation, and will provide a ``last_comments`` method to fetch a given number
   of most recent comments. We also added a class method, to fetch an array of a given number of most 
   recent blog entries.
 
   Now we may use the new functions like this::
       
       >>> e = db.XRecord("blog_entry", 1)
       >>> print e
       Entry: 'Article 1'
       >>> print e.last_comments(2)
       [<xrecord::comment(2)>, <xrecord::comment(3)>]
       >>> print db.Manager.blog_entry.last_entries (2)
       ['Entry: \'Article 1\'', 'Entry: \'Article 2\'']

   The piece of code that makes this happen is the class decorator: ``db.CustomXRecord``. It takes the default
   class for a given table (``blog_entry`` in this case) and derives a new class which inherits it, together
   with the decorated class.

   For this to work the XRecordDatabase object must be instantiated and the connection to the database must
   be active. Therefore it is recommended that all XRecord subclass customizations be made inside the ``Intialize``
   method of a XRecordDatabase subclass, like this::
   	  
     class MyDatabase(XRecordDatabase):
	def Initialize(self):
	    @self.CustomXRecord("blog_entry")
	    class blog_entry:
		"""Do your customizations here"
		pass
	    #Or:
            self.CustomXRecord("category") (some_other_class)
	pass

		    	  

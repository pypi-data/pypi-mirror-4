Extending and customizing XRecords and XSchemas
===============================================

.. module:: xRecord


When an :class:`XRecord` object is created a some things are happening behind the scenes.

First, an :class:`XSchema` definition for the given table is looked for in the XRecordDatabase internal
cache. If it's not found, the database metadata is fetched (from the INFORMATION_SCHEMA) and the XSchema
instance is built.

Next, the library looks for an auto-generated class (a subclass of :class:`XRecord`) for the given table, 
generating it if needed.

Finally an object of this class is instantiated, and, if its primary key value is known a record is fetched
from the backend ::

     #new empty record with all default values
     rec1 = db.XRecord ("blog_entry") 
     #new record with user given values
     rec2 = db.XRecord ( "blog_entry", title="new post", content="blabla" )
     
     #another notation
     rec1 = db.Manager.blog_entry()
     rec2 = db.Manager.blog_entry(title="new post", content="blalbla")

     assert isinstance(rec1, db.XRecordClass)
     assert isinstance(rec1, db.Manager.blog_entry)
     
     #another way of accessing the class
     assert db.XRecordCurrentClass ( "blog_entry" ) is db.Manager.blog_entry

Subclassing XRecord
-------------------

By default the XRecord classes for the tables in your database have the plain functionality of :class:`XRecord`. To
take advantage of object-oriented nature of the ORM, it is possible to extend these classes to add-in your custom
string representation, properties, methods and class methods. This is done using the ``db.CustomXRecord`` decorator and it must be done
after the connection to the database is established. It is therefore recommended that subclassing is done inside the overloaded
``Initialize`` method in your own XRecordDatabase subclass ::

   class MyDatabase(XRecordSqlite):
   	 
	 def Initialize(self):
	     
	     @self.CustomXRecord("author")
	     class any_name_will_be_ok:
	     	   
		   def __repr__(self):
		       return self.name

		   def instance_method(self):
		       do_something_with(self)

		   @classmethod
		   def class_method(cls):
		       do_something_else()

Now we may do the following ::

    db = MyDatabase (name='blog.sqlite')
    author = db.Manager.author(1)
    author.instance_method()	 

    db.Manager.author.class_method()

    print author
    #prints author.name


Subclassing XSchema
-------------------

:class:`XSchema` objects store the table meta data, specifically - column information, primary keys, foreign keys, child references, many-to-many
references and unique indices. They are used when new XRecords are instantiated, when data is saved and fetched, and when special attributes
are accessed.

In our example database to fetch blog entries related to an author we had to write ::

   for entry in author.blog_entry_author:
       print e

This is because the default name of an attribute used to access child references, is build using the <referencing table>_<referencing column>
template. To change this we may subclass the XSchema for the author table and rename this attribute ::

   class MyDatabase(XRecordSqlite):
   	 
	 def Initialize(self):
	     
	     @self.CustomXSchema("author")
	     class any_name_will_be_ok:
	     	   
		   def initialize(self):
		       self.rename_child_reference ( "blog_entry_author", "entries" )
		       do_something_with(self)


Note that we used the ``CustomXSchema`` decorator, instead of the ``CustomXRecord`` used for subclassing XRecords. 

Now it's possible to write ::

   for entry in author.entries:
       print entry


Other method that may be used in an XSchema subclass initialization is ``rename_mtm``, used to rename the attribute under
which a mtm relationship is stored.

XSchema subclasses may also define following methods, to emulate *trigger* behaviour:

   * pre_update ( xrecord, where_conditions, update_values)
   * post_update ( xrecord )
   * pre_insert ( xrecord, insert_values )
   * post_insert ( xrecord )
   * pre_delete ( xrecord )
   * post_delete ( new_xrecord, old_record )


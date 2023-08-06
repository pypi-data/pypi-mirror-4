Database viewer
===============

The ``database viewer`` is a small web application which ships with the
XRecord package. Currently its function is limited to a simple review 
of the database structure with all its table relationships.

Starting the web app
--------------------

Running it is as simple as:

::

  from XRecord import viewer, connection_factory

  viewer.run ( connection_factory ( "sqlite", name="filename" ), address="127.0.0.1", port=3000 )

The ``run`` function accepts a ``connection_factory`` as its first argument - a function yielding
new database connections each time it's called. Its arguments match thos of the ``connect`` function.

If you wish to run the viewer on your subclass of XRecordDatabase, you may do so like this: ::

  from XRecord import viewer
  from myapp import myXRecordDatabase

  viewer.run ( myXRecordDatabase.getFactory ( [arguments] ), address = "127.0.0.1", port=3000 )


 

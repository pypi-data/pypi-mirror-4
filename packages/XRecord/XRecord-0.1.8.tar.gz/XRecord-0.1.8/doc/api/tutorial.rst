Tutorial
========

For this tutorial we will create a simple database for a blog system. While it may be
the most `cliche` example there is (perhaps with the exception of an address book), it
will allow us to demonstrate all features of the *XRecord ORM*. We will use the Sqlite
driver, so it is easier to reproduce on the reader's machine.

.. highlight:: sql

Sample database
---------------

We begin by creating the database, and populating it with some example data.

Its complexity, and the number of triggers is due to the fact
that SQLite does not enforce foreign key contraints. This schema was generated with the excellent
`SQLite foreign key trigger generator <http://rcs-comp.com/site/index.php/view/Utilities-SQLite_foreign_key_trigger_generator>`_,
which made the job as easy as copy & paste :).

.. literalinclude:: src/XRecord/_testing.db.sql
   :language: sql

.. highlight:: python

Connecting to the database
--------------------------

Whew! Now we're ready to start-up python ::

      >>> import XRecord
      >>> db = XRecord.connect("sqlite", name = "blog.db" )

Meta data
---------

Now that we're connected to the database, let's see some debugging info about one of our tables ::

      >>> print db.XSchema("blog_entry").verbose_info
      Table `blog_entry`.
      Columns:
      - content <text>
      - author <integer>
      - id <integer>
      - ts <timestamp>
      - title <text>
      References:
      - author -> author (id)
      Referenced by:
      - id <- entry_category (entry)
      Many-To-Many
      - `entry_category` to category (id) via entry_category

This is what it tell us, about what was read from the database meta-data: 

   * We have 5 columns of the show type
   * The table references the `author` table via the `author` column
   * The table is referenced by the `entry_category` table's column `entry`
   * The table has a many-to-many relationship with the table `category`, via the `entry_category_table`

Querying the database and child references
------------------------------------------

Let's look at some data::

      >>> print db.XArray ( "author" )	
      [<xrecord:author(1)>, <xrecord:author(2)>, <xrecord:author(3)>]

We've fetched the contents of the `author` table as a list of :class:`XRecord` objects. The default python
display isn't very informative, we'll see later how to fix that (`tutorial2`).

Now let's get an `author` record and play with it for a while :) ::

    >>> hemingway = db.XSingle ( "author", "SELECT * FROM author WHERE name like '%hemingway%'" )
    >>> hemingway2 = db.XSingle ( "author", 1 )
    >>> hemingway == hemingway2
    True
    >>> print hemingway
    <xrecord:author(1)>
    >>> print hemingway.id, hemingway.PK, hemingway.SCHEMA.pk
    1 (1,) (u'id',)
    >>> print hemingway.name
    Ernest Hemingway
    >>> print hemingway.blog_entry_author
    [<xrecord:blog_entry(1)>, <xrecord:blog_entry(2)>, <xrecord:blog_entry(3)>]

What happened here? First we retrieved a specific `author` :class:`XRecord` using 2 different methods - with pure SQL, and using
its primary key value of *1* (which we happen to know, by chance ;) ). The two records, although different instances, compare as equal
with the standard python operator. Next we printed the primary key information and the value of the `name` attribute.

Next we accessed the `blog_entry_author` attribute which is a list of referencing records in the `blog_entry` table. The attribute name
is generated using a template: <referencing table name>_<referencing column name>, and also may be customized, which will be discussed later (`tutorial2`).

Let's take a look at the author's blog entries ::

      >>> for entry in hemingway.blog_entry_author:
      ...     print entry, entry.id
      ...     print entry.title
      ...     print entry.entry_category
      ...
      <xrecord:blog_entry(1)> 1
      How I killed myself.
      [<xrecord:category(1)>, <xrecord:category(2)>, <xrecord:category(3)>]
      <xrecord:blog_entry(2)> 2
      How I said "Farewell!" to arms
      [<xrecord:category(2)>]
      <xrecord:blog_entry(3)> 3
      The day I heard the bell toll
      [<xrecord:category(2)>]

Modifying data
--------------

We've iterated over Hemingway's blog entries, show their attributes, and a list of categories assigned to each one.

Let's put some random garbage as the entries' content ::

      >>> for entry in hemingway.blog_entry_author:
      ...     entry.content = hashlib.md5(str(random.random())).hexdigest()
      ...     entry.save()
      ...
      1
      1
      1

Adding many-to-many relationships
---------------------------------

The *1* are the return value of the :method:`XRecord.Save` method, which returns the number of affected rows. Now let's
create a new `category` and assign it to one of Hemingway's entries ::

       >>> entry = hemingway.blog_entry_author[0]
       >>> new_category = db.XRecord ( "category", name="Everything else!")
       >>> new_category.save()
       >>> entry.entry_category.add(new_category)

We took an entry from the author's list, created the new category, saved it (important) and put it in relationship with the
entry using the virtual method `entry_category.add`. Try it again ::
	
	>>> entry.entry_category.add(new_category)
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "db.py", line 237, in __setattr__
	       via_record.Insert()
	  File "db.py", line 438, in Insert
               retval = self.DB.InsertQuery ( self.DB.BuildInsertSQL ( self.TABLE, **insert) )
	  File "db.py", line 911, in InsertQuery
	      with self.Query(sql,*args) as result:
          File "/usr/local/lib/python2.6/contextlib.py", line 16, in __enter__
	      return self.gen.next()
          File "db.py", line 860, in Query
	      raise self.ErrorTranslation(e)
	  db.DatabaseError: columns entry, category are not unique

The database backend complains about a contraint violation. Now let's see the entry's category list ::
    
    >>> print entry.entry_category
    [<xrecord:category(1)>, <xrecord:category(2)>, <xrecord:category(3)>]

The new category does not appear in it. The reason for this is that XRecord instances cache the foreign key, child and 
many-to-many relationships. When a new related object is added in a mtm relationship, the cached list remains the same
unless explicitly purged like this::

    >>> del entry.entry_category
    >>> print entry.entry_category
    [<xrecord:category(1)>, <xrecord:category(2)>, <xrecord:category(3)>, <xrecord:category(10)]

Now we delete the new category::

   >>> new_category.delete()
   >>> del entry.entry_category
   >>> print entry.entry_category
   [<xrecord:category(1)>, <xrecord:category(2)>, <xrecord:category(3)>]
   
and the database triggers take care of the rest.

Accessing Foreign Key references
--------------------------------

It is also easy to access records referenced by a record we are working with ::

   >>> entry
   <xrecord:blog_entry(1)>
   >>> entry.author
   1
   >>> entry.author.ref
   <xrecord:author(1)>
   >>> entry.author.ref.id
   1
   >>> entry in entry.author.ref.blog_entry_author
   True

Word of caution. The ``entry.author`` attribute is an object of class XRecordFK. Even though, when converted to its string
representation it looks like the actual value of the corresponding column, it is safer to access this value by using ``entry.author.value``.
That way you can be certain your are working with the value returned by the backend. When setting this attributes value, you can use 
``entry.author = new_val`` as well as ``entry.author.value = new_val`` - they are equivalent. ``new_val`` may be the actual value
for the column, or an instance of :class:`XRecord` for the referenced table.


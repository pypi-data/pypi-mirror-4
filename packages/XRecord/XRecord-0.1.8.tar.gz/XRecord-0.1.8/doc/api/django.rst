Integrating with Django
=======================

XRecord integrates seamlessly with the Django Web framework. 


How?
----

Just use it, there is no magic to it, no tricks. You'd probably want to subclass XRecordDatabase, to customize your
objects behaviour. ::
  
  from XRecord.mysql import XRecordMySQL

  class AppDatabase(XRecordMySQL):
  	connection_defaults = { 'name' : 'blog', 'user' : 'blogger' }
	pass
        
  	def Initialize(self):
	    ### customization.... 
            ### customization....
            pass

 
Then use it inside a view function: ::
     
  from django.shortcuts import render_to_response
  from django.template import RequestContext
  from mydatabase import AppDatabase

  def view_function (request):
    try:
      db = AppDatabase.getInstance()
      authors = db.XArray ( "author" )
      return render_to_response ( 'view_template.html', {'authors' : authors }, context_instance = RequestContext(request) )
    except db.Error, e:
      return render_to_response ( 'view_error.html', {'error' : e }, context_instance = RequestContext(request) )


And your template ``view_template.html``, could look a little like this:

::

	<pre>
	{% for author in authors %}
	   {{ author.name }}
	   {% for blog_entry in author.blog_entry_authors %}
	   entry: {{ blog_entry.title }}
	      categories: {% for category in blog_entry.entry_category %} {{ category.name }} {% endfor %}
	   {% endfor %}
	{% endfor %}
	</pre>


Performance issues
^^^^^^^^^^^^^^^^^^

There is something about the way XRecord works, that raises questions about its performance in a high-load web
environment: every time XRecordDatabase is instantiated, it reads the meta-data from the backend. For
normal, long-running applications this is has negligable impact on performance, but when it is happening
once for every single web request, it can be significant.

XRecord has a solution for this problem - *meta-data caching*. The XRecordDatabase class has two methods
``ReadMetaDataCache`` and ``WriteMetaDataCache``, which read and write the meta-data information from a 
file on the disk. The call to first may be placed inside the ``Initialize`` method, the second has to be
run every time something in your database structure changes. 

::

  def Initialize(self):
    #....
    self.ReadMetaDataCache('/var/lib/blog_database.metadata')

::

  #eg. inside some "update" script:
  db.WriteMetaDataCache ('/var/lib/blog_database.metadata')

Why?
----

In fact, integration with Django was one of our main concerns, when we designed and implemented XRecord.
When we first attempted to port some of our applications to use Django, the situation was as follows:

 * we had a big, complex MySQL database, with a frequently changing structure,
 * we had a number of Python applications that used this database,
 * we had a big, ugly PHP web app, which also used this database,
 * we had a simple thin db-api Python library named XRecord used by the Python applications.

We decided to port the web app to Django, so it seemed what we needed to do was:

 #. use Django's `inspectdb` feature to generate the model from our db,
 #. rewrite the web app
 #. later rewrite the Python applications to use the Django model, so the project code is clean.

Step ``1`` turned out to be problematic, but not impossible. The Django introspection engine had some issues
detecting all the relationships between tables, so they had to be completed by hand. 

Step ``2`` seemed to be going fine, some working prototypes were produced, but then we had to modify
the database definition, and there was no other way, but to 
 
 * modify the mysql database 
 * make the corresponding changes to the model, by hand

As lovers of the DRY principle, we were totally dissatisfied with the way this was turning out. So we quickly
moved to step ``3``, to see if any other problems would surface. Without going into details - we understood 
that Django was simply not a good tool to write applications that are 
not meant to run in a web environment. We also understood, that it does not have to be such a tool, and probably,
should not be, since it had "Web framework" in the name.

So we decided to take a different approach:

 #. modify XRecord so it can be used inside Django
 #. rewrite the web app
 #. leave the other Python apps as they are, tested and working

which is good because we have a single database layer for both the web-application and the non-web-applications. DRY.

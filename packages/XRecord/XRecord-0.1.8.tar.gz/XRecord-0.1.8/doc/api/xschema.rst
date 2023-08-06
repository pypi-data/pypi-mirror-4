Handling meta-data
==================

TODO :)

.. automodule:: xRecord

XSchema
-------

.. autoclass:: XSchema
   
   .. automethod:: rename_mtm
   .. automethod:: rename_child_reference
   .. automethod:: has_child
   .. automethod:: has_mtm
 
   .. automethod:: has_column
   .. automethod:: get_child
   .. automethod:: get_mtm
   .. automethod:: column_list
   .. automethod:: columns
   
   .. automethod:: pre_update
   .. automethod:: post_update
   .. automethod:: pre_insert
   .. automethod:: post_insert
   .. automethod:: pre_delete
   .. automethod:: post_delete
   
   .. automethod:: initialize
   
   .. autoattribute:: null
   .. autoattribute:: default
   .. autoattribute:: verbose_info  


Customizing XSchema
-------------------

::

	@db.CustomXSchema("author")
	class blog_entry:
	      def __repr__(self):
	      	  return self.name

	      def initialize(self):
	      	  self.rename_child_reference ( "blog_entry_author", "blog_entries")

  	
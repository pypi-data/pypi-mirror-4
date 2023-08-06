from XRecord.sqlite import XRecordSqlite
import sys, hashlib, random
db = XRecordSqlite.getInstance ( name = "blog.sqlite" )

print db.XArray ( "author" )

hemingway = db.XSingle ( "author", "SELECT * FROM author WHERE name like '%hemingway%'" )
print hemingway
print hemingway.id, hemingway.PK, hemingway.SCHEMA.pk
print hemingway.name
print hemingway.blog_entry_author

for entry in hemingway.blog_entry_author:
    print entry, entry.id
    print entry.title
    print entry.entry_category
    entry.content = hashlib.md5(str(random.random())).hexdigest()
    entry.Save()

for entry in hemingway.blog_entry_author:
    print entry.title
    for category in entry.entry_category:
        print " - in category", category.name

entry = hemingway.blog_entry_author[0]
new_category = db.XRecord ( "category", name="Everything else!")
new_category.Save()
entry.add_entry_category = new_category
del entry.entry_category
print entry.entry_category
new_category.Delete()
del entry.entry_category
print entry.entry_category

db.Close()

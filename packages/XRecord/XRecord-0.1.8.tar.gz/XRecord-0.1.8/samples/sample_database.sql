BEGIN TRANSACTION;
CREATE TABLE author ( id integer PRIMARY KEY autoincrement, name text);
INSERT INTO "author" VALUES(1,'Ernest Hemingway');
INSERT INTO "author" VALUES(2,'Oscar Wilde');
INSERT INTO "author" VALUES(3,'George Byron');
DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('author',3);
INSERT INTO "sqlite_sequence" VALUES('category',3);
INSERT INTO "sqlite_sequence" VALUES('blog_entry',9);
CREATE TABLE blog_entry (id integer PRIMARY KEY autoincrement,
       author integer constraint be_1 REFERENCES author (id) ON DELETE cascade, title text, content text, ts timestamp );
INSERT INTO "blog_entry" VALUES(1,'How I killed myself.',NULL,1,NULL);
INSERT INTO "blog_entry" VALUES(2,'How I said "Farewell!" to arms',NULL,1,NULL);
INSERT INTO "blog_entry" VALUES(3,'The day I heard the bell toll',NULL,1,NULL);
INSERT INTO "blog_entry" VALUES(4,'How I sent Harold on a pilgrimage',NULL,2,NULL);
INSERT INTO "blog_entry" VALUES(5,'Who is this Giuar?',NULL,2,NULL);
INSERT INTO "blog_entry" VALUES(6,'My Byronic Hero',NULL,2,NULL);
INSERT INTO "blog_entry" VALUES(7,'About my friend Dorian',NULL,3,NULL);
INSERT INTO "blog_entry" VALUES(8,'Screw being ernest',NULL,3,NULL);
INSERT INTO "blog_entry" VALUES(9,'Man of no importance',NULL,3,NULL);
CREATE TABLE category (id integer PRIMARY KEY autoincrement, name text );
INSERT INTO "category" VALUES(1,'Poems');
INSERT INTO "category" VALUES(2,'Prose');
INSERT INTO "category" VALUES(3,'Documentary');
CREATE TABLE entry_category (
       entry integer constraint ce_1 REFERENCES blog_entry(id) ON DELETE cascade,
       category integer constraint ce_2 REFERENCES category(id) ON DELETE cascade, PRIMARY KEY (entry, category) );
INSERT INTO "entry_category" VALUES(1,3);
INSERT INTO "entry_category" VALUES(2,2);
INSERT INTO "entry_category" VALUES(1,2);
INSERT INTO "entry_category" VALUES(3,2);
INSERT INTO "entry_category" VALUES(4,1);
INSERT INTO "entry_category" VALUES(5,1);
INSERT INTO "entry_category" VALUES(6,2);
INSERT INTO "entry_category" VALUES(7,1);
INSERT INTO "entry_category" VALUES(8,2);
INSERT INTO "entry_category" VALUES(9,2);
INSERT INTO "entry_category" VALUES(9,3);
CREATE TRIGGER fki_blog_entry_author_author_id
BEFORE INSERT ON [blog_entry]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "blog_entry" violates foreign key constraint "fki_blog_entry_author_author_id"')
  WHERE NEW.author IS NOT NULL AND (SELECT id FROM author WHERE id = NEW.author) IS NULL;
END;
CREATE TRIGGER fku_blog_entry_author_author_id
BEFORE UPDATE ON [blog_entry] 
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "blog_entry" violates foreign key constraint "fku_blog_entry_author_author_id"')
      WHERE NEW.author IS NOT NULL AND (SELECT id FROM author WHERE id = NEW.author) IS NULL;
END;
CREATE TRIGGER fkdc_blog_entry_author_author_id
BEFORE DELETE ON author
FOR EACH ROW BEGIN 
    DELETE FROM blog_entry WHERE blog_entry.author = OLD.id;
END;
CREATE TRIGGER fki_entry_category_entry_blog_entry_id
BEFORE INSERT ON [entry_category]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "entry_category" violates foreign key constraint "fki_entry_category_entry_blog_entry_id"')
  WHERE NEW.entry IS NOT NULL AND (SELECT id FROM blog_entry WHERE id = NEW.entry) IS NULL;
END;
CREATE TRIGGER fku_entry_category_entry_blog_entry_id
BEFORE UPDATE ON [entry_category] 
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "entry_category" violates foreign key constraint "fku_entry_category_entry_blog_entry_id"')
      WHERE NEW.entry IS NOT NULL AND (SELECT id FROM blog_entry WHERE id = NEW.entry) IS NULL;
END;
CREATE TRIGGER fkdc_entry_category_entry_blog_entry_id
BEFORE DELETE ON blog_entry
FOR EACH ROW BEGIN 
    DELETE FROM entry_category WHERE entry_category.entry = OLD.id;
END;
CREATE TRIGGER fki_entry_category_category_category_id
BEFORE INSERT ON [entry_category]
FOR EACH ROW BEGIN
  SELECT RAISE(ROLLBACK, 'insert on table "entry_category" violates foreign key constraint "fki_entry_category_category_category_id"')
  WHERE NEW.category IS NOT NULL AND (SELECT id FROM category WHERE id = NEW.category) IS NULL;
END;
CREATE TRIGGER fku_entry_category_category_category_id
BEFORE UPDATE ON [entry_category] 
FOR EACH ROW BEGIN
    SELECT RAISE(ROLLBACK, 'update on table "entry_category" violates foreign key constraint "fku_entry_category_category_category_id"')
      WHERE NEW.category IS NOT NULL AND (SELECT id FROM category WHERE id = NEW.category) IS NULL;
END;
CREATE TRIGGER fkdc_entry_category_category_category_id
BEFORE DELETE ON category
FOR EACH ROW BEGIN 
    DELETE FROM entry_category WHERE entry_category.category = OLD.id;
END;
COMMIT;

spycouch
========

Simple Python API for CouchDB 


Python library for easily manage CouchDB.

Compared to ordinarily available libraries on web, works with the latest version CouchDB - 1.2.1

Functionality
-------------
> Create a new database on the server

> Deleting a database from the server

> Listing databases on the server

> Database information

> Database compression

> Create map view

> Map view


> Listing documents in DB

> Get document from DB

> Save document to DB

> Delete document from DB

> Editing of a document


example of use
--------------

from spycouch import *

couch = Couch('localhost')

couch.create_db("test-db")

print couch.list_of_dbs()

print couch.info_db("test-db")

couch.compact_db("test-db")

document = '{"code" : "null"}'

couch.save_doc("test-db", document, "foo")

couch.save_doc("test-db", document, "bar")

print couch.list_of_docs("test-db")

couch.save_doc("test-db", document)

print couch.list_of_docs("test-db","limit=1")

print couch.open_doc("test-db", "foo")

couch.delete_doc("test-db", "foo")

document = {"code":"err"}

couch.update_doc("test-db", document, "bar")

map_funcs = {}

map_funcs["err"] = "function(doc) {if (doc.code == 'err')  emit(doc._id, null)}"

map_funcs["code"] = "function(doc) {if (doc.code == 'null')  emit(doc._id, null)}"

couch.create_view("test-db", "javascript", "test-db-view", map_funcs)

print couch.map("test-db", "test-db-view", "err", 5)

couch.delete_db("test-db")



> name: Simple Python API for CouchDB 

> autor: Černý Jan

> version: 0.1

> license: viz. LICENSE
# -*- coding: utf-8 -*-
# čžřě+áýčíáý+í
"""
name: Simple Python API for CouchDB 
autor: Černý Jan
email: cerny.jan@hotmail.com
version: 0.1
license: viz. LICENSE


example of use:

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
"""

import  sys
import httplib, json
import httplib2
import urllib2

class Couch:
    """
    Class of Simple Python API for CouchDB 
    """
    def __init__(self, host, port=5984):
        """
        Constructor of Couch class
        
        @type  host: string
        @param host: Location of CouchDB server - ordinarily is localhost.
        @type  port: number
        @param port: Number of CouchDB server port.
        """
        self.host = host
        self.port = port
        
    def connect(self):
        """
        Http connection
        
        @rtype:   HTTPConnection instance
        @return:  Transaction with an HTTP server.
        """
        return httplib.HTTPConnection(self.host, self.port)
        
    # Http basic methods for communicating with DB
    
    def get(self, uri):
        """
        Method GET
        
        @type  uri: string
        @param uri: Uniform Resource Identifier.
        @rtype:   object
        @return:  Response for request.
        """
        con = self.connect()
        headers = {"Accept": "application/json"}
        con.request("GET", uri, None, headers)
        return con.getresponse()
    
    def post(self, uri, body):
        """
        Method POST
        
        @type  uri: string
        @param uri: Uniform Resource Identifier.
        @rtype:   object
        @return:  Response for request.
        """
        con = self.connect()
        headers = {"Content-type": "application/json"}
        con.request('POST', uri, body, headers)
        return con.getresponse()
    
    def put(self, uri, body):
        """
        Method PUT
        
        @type  uri: string
        @param uri: Uniform Resource Identifier.
        @rtype:   object
        @return:  Response for request.
        """
        con = self.connect()
        if len(body) > 0:
            headers = {"Content-type": "application/json; charset=UTF-8"}
            con.request("PUT", uri, body, headers)
        else:
            con.request("PUT", uri, body)
        return con.getresponse()
    
    def delete(self, uri):
        """
        Method DELETE
        
        @type  uri: string
        @param uri: Uniform Resource Identifier.
        @rtype:   object
        @return:  Response for request.
        """
        con = self.connect()
        con.request("DELETE", uri)
        return con.getresponse()
                                   
    #DB operations     
    
    def create_db(self, db_name):
        """
        Create a new database on the server
        
        @type  db_name: string
        @param db_name: Name of DB.
        @rtype:   bool
        @return:  True or False.
        """
        try:
            response = self.put(''.join(['/', db_name, '/']), "")        
            dict_response = json.loads(response.read())
            if "ok" in dict_response:
                return True
            else:
                print dict_response['error']+":"+dict_response['reason']
                return False
        except IOError:
            print sys.exc_info()[0]
            return False
        
    def delete_db(self, db_name):
        """
        Deleting a database from the server
        
        @type  db_name: string
        @param db_name: Name of DB.
        @rtype:   bool
        @return:  True or False.
        """
        try:
            response = self.delete(''.join(['/', db_name, '/']))
            dict_response = json.loads(response.read()) 
            if "ok" in dict_response:
                return True
            else:
                print dict_response['error']+":"+dict_response['reason']
                return False
        except IOError:
            print sys.exc_info()[0]
            return False
        
    def list_of_dbs(self):
        """
        Listing databases on the server
        
        @rtype:   array
        @return:  List of DBs.
        """
        try:
            response = self.get('/_all_dbs')
            str_response = json.dumps(json.loads(response.read()), sort_keys=True, indent=4)
            list_response = eval(str_response)
            return list_response
        except IOError:
            print sys.exc_info()[0]
            return []
            
    def info_db(self, db_name):
        """
        Database information
        
        @type  db_name: string
        @param db_name: Name of DB.
        @rtype:   dictionary
        @return:  Database information as dictionary.
        """
        try:
            response = self.get(''.join(['/', db_name, '/']))
            dict_response = json.loads(response.read()) 
            if "error" in dict_response:
                print dict_response['error']+":"+dict_response['reason']
                return {}
            else:
                return dict_response
        except IOError:
            print sys.exc_info()[0]
            return {}
        
    def compact_db(self, db_name):   
        """
        Database compression
        
        @type  db_name: string
        @param db_name: Name of DB.
        @rtype:   bool
        @return:  True or False.
        """
        data = {}
        try:
            request = urllib2.Request("http://"+self.host+":"+str(self.port)+"/"+db_name+'/_compact')
            request.add_header('Content-Type', 'application/json')
            response = urllib2.urlopen(request, json.dumps(data))
            if "ok" in str(response.read(11)):
                return True
            else:
                return False
        except IOError:
            print sys.exc_info()[0]
            return False
            
    def create_view(self, db_name, language, design_name, dict_map_funcs):
        """
        Create map view
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  language: string
        @param language: Language for map.
        @type  design_name: string
        @param design_name: Name of design view.
        @type  dict_map_funcs: dictionary
        @param dict_map_funcs: Key -> name of views, Value -> map function.
        @rtype:   bool
        @return:  True or False.
        """
        design_name = "_design/"+design_name
        design = "{"+'"language"'+":"+'"'+language+'"'+","+'"views"'+":"+"{"   
        for key, value in dict_map_funcs.iteritems():
            design += ('"'+key+'"'+":"+"{"+'"map"'+":"+'"'+value+'"'+"}"+",")
        design = design[0:len(design)-1] + ("}"+"}")
        if self.save_doc(db_name, design, design_name):
            return True
        else:
            return False
        
    def map(self, db_name, design_name, view_name, limit=None):
        """
        Map view
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  design_name: string
        @param design_name: Name of design view.
        @type  view_name: string
        @param view_name: Name of view.
        @type  limit: number
        @param limit: Number of records returned, optional parameter.
        @rtype:   dictionary
        @return:  Map view of documents as dictionary.
        """
        if limit == None:
            uri = "http://"+self.host+":"+str(self.port)+"/"+ db_name +"/_design/"+design_name+"/_view/"+view_name
        else:
            uri = "http://"+self.host+":"+str(self.port)+"/"+ db_name +"/_design/"+design_name+"/_view/"+view_name+"?limit="+str(limit)
        try:
            response = urllib2.urlopen(uri)
            return json.loads(response.read())
        except IOError:
            print sys.exc_info()[0]
            return {}
        
    # Operations with documents
    
    def list_of_docs(self, db_name, options=None):
        """
        Listing documents in DB
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  options: string
        @param options: Parameters, optional parameter.
        @rtype:   array
        @return:  List of documents.
        """
        if options == None:
            uri = ''.join(['/', db_name, '/', '_all_docs'])
        else:
            uri = ''.join(['/', db_name, '/', '_all_docs',  '/?', options])
        try:
            response = self.get(uri)
            dict_response = json.loads(response.read()) 
            if "error" in dict_response:
                print dict_response['error']+":"+dict_response['reason']
                return {}
            else:
                list_docs = []
                for dict_doc in dict_response['rows']:
                    list_docs.append(dict_doc['id'])
                return list_docs            
        except  IOError:
            print sys.exc_info()[0]
            return []
        
    def open_doc(self, db_name, doc_id):
        """
        Get document from DB
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  doc_id: string
        @param doc_ids: Document identifier.
        @rtype:   dictionary
        @return:  Document as dictionary.
        """
        try:
            response = self.get(''.join(['/', db_name, '/', doc_id,]))
            dict_response = json.loads(response.read()) 
            if "error" in dict_response:
                print dict_response['error']+":"+dict_response['reason']
                return {}
            else:
                return dict_response
        except IOError:
            print sys.exc_info()[0]
            return {}
        
    def save_doc(self, db_name, body, doc_id=None):
        """
        Save document to DB
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  body: string
        @param body: Body of the document.
        @type  doc_id: string
        @param doc_ids: Document identifier, optional parameter (with own name of document).
        @rtype:   bool
        @return:  True or False.
        """
        try:
            if doc_id:
                response = self.put(''.join(['/', db_name, '/', doc_id]), body)
            else:
                response = self.post(''.join(['/', db_name, '/']), body)
            dict_response = json.loads(response.read())
            if "ok" in dict_response:
                return True
            else:
                print dict_response['error']+":"+dict_response['reason']
                return False
        except IOError:
            print sys.exc_info()[0]
            return False
        
    def delete_doc(self, db_name, doc_id):
        """
        Delete document from DB
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  doc_id: string
        @param doc_ids: Document identifier.
        @rtype:   bool
        @return:  True or False.
        """
        try:
            dict_response = self.open_doc(db_name, doc_id)
            if "error" in dict_response:
                print dict_response['error']+":"+dict_response['reason']
                return False
            else:
                self.delete(''.join(['/', db_name, '/', doc_id, '?rev=', dict_response['_rev']]))
                return True
        except KeyError:
            print sys.exc_info()[0]
            return False
        
    def update_doc(self, db_name, values, doc_id):
        """
        Editing of a document
        
        @type  db_name: string
        @param db_name: Name of DB.
        @type  values: dictionary
        @param values: Content of change.
        @type  doc_id: string
        @param doc_ids: Document identifier.
        @rtype:   bool
        @return:  True or False.
        """
        dict_response = self.open_doc(db_name, doc_id)
        if len(dict_response) > 0:
            for key, value in values.iteritems():
                dict_response[key] = value
            body = json.dumps(dict_response)
            self.put(''.join(['/', db_name, '/', doc_id]), body)
            return True
        else:
            return False

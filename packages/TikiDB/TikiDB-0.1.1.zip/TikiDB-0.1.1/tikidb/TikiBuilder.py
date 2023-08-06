"""Module usedto build a ZODB that will be used by the TikiWare WebApp Framework"""

from TikiDB import DB
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime

class Builder(object):
    """
    Main class to be used to create the database.  requires a tikiDB.DB to be
    passed.  All methods that commit data must be explicitly committed by
    transaction.commit() after being performed.

    """
    
    def __init__(self,db):
        """
        ensures that a TikiDB.DB is passed and checks it for the base  containers
        
        :param db: passed TikiDB.DB
        :type db: TikiDB.DB()

        """        
        self.db = db       
        if not self.db.root.has_key('index_listing'):
            self.db.root['index_listing'] = OOBTree()
        if not self.db.root.has_key('object_definitions'):
            self.db.root['object_definitions'] = OOBTree()
        if not self.db.root.has_key('database_docs'):
            self.db.root['database_docs']= PersistentMapping({})
            self.db.root['database_docs']['name']=''
            self.db.root['database_docs']['version_number']='1.0'
            self.db.root['database_docs']['version_date']=repr(datetime.now())
            self.db.root['database_docs']['description']=''
            
            
            

    def getIndexes(self):
        """
        Return a list of all indexes

        """
        return dict(self.db.root['index_listing'])
    
    def getContainers(self):
        """
        return a list of all containers

        """
        return self.db.root.keys()
    
    def getObjectDefinitions(self):
        """
        Return a dict of the object definitions

        """
        return dict(self.db.root['object_definitions'])
    
    def generateDatabaseDocs(self,doc_type='markdown'):
        """
        generate database document.  this will contain information on
        the containers, objects and indexes that are available in the
        database
        :param doc_type: is the type data returned. valid types are: markdown, html, print: pretty print?
        :type  doc_type: string
        
        """
        if doc_type == 'markdown':
            #create the markdown database docs
            pass
            
            
    def create_container(self,name,rebuild=False):
        """
        creates a containter to house data objects and adds an object to the
        index_listing container
        
        :param name: The name of the conainter to be created. should be a plural
                     of the object (i.e. people for an container to house
                     person objects, recipies for a container to house recipe
                     objects, etc...)
        :type name: String
        
        """
        if self.db.root.has_key(name):
            if not rebuild:
                raise
        self.db.root[name] = IOBTree()
        self.db.root['index_listing'][name]=PersistentMapping()        

    def create_object_definition(self, obj_name,obj_container,obj_fields,
                                 obj_desc,version_number=1.0,version_date=None):
        """
        creates the data definition of an object. the name of the object
        definition should be a singular object.
        
        :param obj_name: name of the object for which the definition will be created
        :type obj_name: String
        :paramobj_container: name of the container where the objects will be stored
        :type obj_container: String
        :param obj_fields: dictionary of required fields.  The key is name of field
                           value is the data type stored. if blank any data is accepted
        :type obj_fields: Dict
        :param obj_desc: a brief description of the object
        :type obj_desc: String
        :param version_number: the revision of the object. this should be incremented
                               for every change there is to an object definition
                               to allow for updating of the object
        :type version_number: Float
        :param version_date: the date of the version. if None it becomes the current date
        :type version_date: String (formated in standard python datetime)

        """
        obj = {}
        for k,v in obj_fields.iteritems():
            obj[k] = v
        if not version_date:
            version_date = str(datetime.now())
        if self.db.root['object_definitions'].has_key(obj_name):
            raise
        #persistent mapping of fields that have indexes. used to update indexes
        #when a field changes or ojbect is added. key = field_name
        #value = index container name. this will be updated when indexes are
        #created.
        indexed_fields = PersistentMapping({}) 
        self.db.root['object_definitions'][obj_name]=PersistentMapping({'container':obj_container,
                                                                        'definition':obj,
                                                                        'description':obj_desc,
                                                                        'version_number':version_number,
                                                                        'version_date':version_date,
                                                                        'indexed_fields':indexed_fields})
        
    def makeIndex(self,index_name,index_type,index_container,index_field,
                  index_description,reindex=False):
        """
        calls the makeIndex method of the passed TikiDB.DB() to create an index.
        Refer to the doc string of the TikiDB.DB.makeIndex() for more info

        """
        self.db.makeIndex(index_name,index_type,index_container,index_field,
                          index_description,reindex=False)
            
            
            
if __name__ == "__main__":
    
    db = DB('test.zodb')
    builder = Builder(db)
    builder.create_container('tests')
    builder.create_object_definition('test','tests',{'name':'','desc':'','module':''},'data about a test for the database')
    builder.makeIndex('i_module_name_to_tests','IOBTree','tests','module','list of test ids that test a module')
    
    

from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from BTrees.IOBTree import IOBTree,IOTreeSet,IOSet
from BTrees.OOBTree import OOBTree,OOTreeSet,OOSet
import ZODB
import ZODB.FileStorage
from datetime import datetime
from time import sleep
import re,exceptions

#define custom exceptions for module
class TikiWareIndexError(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
    
class DB(object):
    def __init__(self,db_name):
        """
        boilder plate code to setup the ZODB database connection

        :param db_name: the name of the db to be connected. can be a path
        :type db_name: String (filename or path)

        """
        self.storage = ZODB.FileStorage.FileStorage(db_name)
        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root()
        self.list_types = OOSet((PersistentList,IOTreeSet,IOSet,OOTreeSet,OOSet,list))
        self.dict_types = OOSet((PersistentMapping,IOBTree,OOBTree,dict))

    def close(self):
        """
        Close the database connection

        """
        self.connection.close()
        self.db.close()
        self.storage.close()

    def pack(self,t=None, days=0):
        """
        pack the database using zodb pack

        """
        self.db.pack()
    
    def get_next_id(self,obj_name):
        """
        get the next object ID from a data container
        
        :param obj_name: the name of the container
        :type obj_name: string

        :returns: the next integer ID for a container

        """
        #see if container exists
        if self.root.has_key(obj_name):
            try:
                ret = self.root[obj_name].maxKey() + 1
        
            except Exception as e:
                if isinstance(e,ValueError):
                    ret = 1
                else:
                    ret = e.message                
        else:
            ret = 'Data Container does not exist'
        return ret 
                
            
    def create_object(self,obj_name,data):
        """
        Create an object with data from the object_definitions container
        
        :param obj_name: the name of the definition that will create the object
        :type obj_name: string
        :param data: key/value pairs of data for the object.  all of the keys
                     in the object definition must be satisfied by the keys in
                     the data
        :type data: dict or similar

        :returns: added for ok otherwise error message

        """
        #verify object exists in the object definitions
        has_def = self.root['object_definitions'].has_key(obj_name)
        if has_def:
            value = self.root['object_definitions'][obj_name]
            #check for all requried values if not raise error
            required_values = dict(value['definition'])
            for k,v in value['definition'].iteritems():
                #add code here to check the data type.
                #if it is a class the data will be and attribute named data
                #if dict is will do else.  may add functionality for lists and
                #other types of data at a later time.
                #if isinstance(data,object):
                    #get data attribute
                #else:
                if data.has_key(k):
                    #verify the field is the correct format
                    #if data[k] == 'list'
                    required_values.pop(k)
            if required_values:
                #missing values do not add
                return Exception
            #get next id for object
            #obj_id = self.root[value['container']].maxKey() + 1
            
            #add object to container
            #try loop
            ok =''
            for x in range(0,5):
                try:
                    #get next id for object
                    obj_id = self.get_next_id(value['container'])
                    #check id is not overwriting data due to multiconnections
                    if self.root[value['container']].has_key(obj_id):
                        raise
                    else:
                        #if no id exists add it
                        ok = self.root[value['container']].insert(obj_id,data)
                        break
                except:
                    sleep(.1)
                    pass
            if not ok:
                return ok
            else:
                return 'added'
        else:
            return 'object has no definition'
                            
              
    def findObjectIdByField(self,obj,search_criteria):
        """
        find objects by looping through all data. obj is the containter, kwargs
        is the name and value of the field to be searched. returns a list of
        id numbers for the container. 
        This is for non-indexed searches.  may be slow due to looping through
        data sets but may be used to build ad hoc queries.
        
        :param obj: the data object type to be found
        :type obj: string
        :param search_criteria: a list or tuple of dicts.  Key is the field
                                value is the search value. if value is None
                                the key is an object that is to be searched.
                                this allows for searching of sub-objects
        :type field: a list or tuple of dicts
        :param value: the value to search for can use wildcards.  % for all
                      characters before or after it.  ? for a single character
        :type value: string
        :returns: list of object ids(keys) which can be used to pull data
        
        """
        #check if field is the key for a containter
        container = self.root['object_definitions'][obj]['container']
        #print container
        if container:
            #check if the serach is for a sub-object and get a list of them
            obj_list = []
            for i in search_criteria:
                field,value=i.iteritems().next()
                if not value:
                    obj_list.append(field)
                else:
                    break
            #modify field for wildcards
            try:
                #check for wild card % and  do appropriate search look for match using re
                if value[:1] =='%':
                    pre_p = r"^(^.*)"                    
                else:
                    pre_p = r"^"
                if value[-1:] == '%':
                    post_p = r"(.*)$"
                else:
                    post_p= r"$"
                p = r"%s%s%s"%(pre_p,value.replace('%',''),post_p)

                #look for wild card ? and replace a single character
                if p.find('?')>-1:
                    p = p.replace('?','(.{1})')
                #print p
                #value = re.compile(r"^%s$"%p)
                #try
                value = re.compile(r'%s'%p)
                #print value.pattern
            except Exception as e:
                print 'can not make pattern'
                print e
                print e.__class__
                return e
                
            try:
                results = []
                for k,v in self.root[container].iteritems():
                    #if the search is on a subobject get the object and
                    #make it the search object
                    for obj in obj_list:
                        v = v[obj]
                    try:
                        #is a dictionary type
                        if self.dict_types.has_key(type(v)):                    
                            #field is a list or a value
                            if self.list_types.has_key(type(v[field])):
                                for i in v[field]:
                                    if re.match(value,i):
                                        results.append(k)
                                        break
                            else:
                                if re.match(value,v[field]):
                                    results.append(k)
                        #is a list type        
                        elif self.list_types.has_key(type(v)):
                            for i in v:                                
                                if re.match(value,i):
                                    results.append(k)
                                    break
                        #is something else
                        else:
                            if re.match(value,v):
                                results.append(k)
                                
                    except Exception as e:
                        if e.__class__ != exceptions.TypeError:
                            raise e
                            
            except Exception as e:
                print 'error searching'
                print k,v,field,value
                print e
                print e.args
                print e.__class__
                return e
        else:
            print 'can not find container'
            return
        return results                
            
    def sortData(self,data,sort_fields,order='asc'):
        """
        sort a list of data based on the sort fields. uses eval to create the lambda.
        Not sure if there is a better way....
        
        :param data: a list of dictionary data
        :type data: dict
        :param sort_fields: a list of field names in the order to be sorted. first is most important
        :type sort_fields: list
        :param order: the order the data should be sorted. asc= ascending otherwise descending
        :type order: string

        returns a list of dictionaries

        """
        s_lambda = 'lambda k:('
        for i in sort_fields:
            s_lambda='%sk["%s"],'%(s_lambda,i)
        s_lambda = s_lambda[:-1]+")"
        if order !='desc':
            order = False
        else:
            order = True            
        print s_lambda
        data.sort(key=eval(s_lambda),reverse=order)
        return data
        
    def makeIndex(self,index_name,index_type,index_container,index_field,
                  index_description,reindex=False):
        """
        Create an index of object IDs (integers) for objects in a container. if successful
        it will update the index_listing container and the appropriate object in
        the object_definitions container
        
        :param index_name: is the name of the index
        :type index_name: String
        :param index_type: declares the type of btree to use. If keys are
                           integer use IOBTree, otherwise use OOBTree
        :type index_type: String
        :param index_container: the name container to be indexed
        :type index_container: String
        :param index_field: The name of field to be indexed. this will be the
                            key of the newly created index
        :type index_field: String
        :param reindex: recreate index if set to True
        :type reindex: Boolean
        :param index_description: is the narrative of what the index is used for


        """
        #set the index name to begin with _index_
        index_name = 'index_'+index_name
        #verify if index exists
        if self.root.has_key(index_name):
            if reindex:
                #delete index and recreate
                err = self.root.pop(index_name, None)
            else:
                #raise error
                raise TikiWareIndexError("Index Exists")
        #create index container
        if index_type == 'OOBTree':
            self.root[index_name] = OOBTree()
        elif index_type == 'IOBtree':
            self.root[index_name] = IOBTree()
        #check passed data to ensure the operation can be done
        for k,v in self.root['object_definitions'].iteritems():
            if v['container'] == index_container:
                obj_name = k
                
        print obj_name,index_field
        if self.root.has_key(index_container):
            if self.root['object_definitions'][obj_name]['definition'].has_key(index_field):
                pass
            else:
                raise TikiWareIndexError("Invalid index_field")
        else:
            raise TikiWareIndexError("Invalid index_container")
        #create the index
        for k,v in self.root[index_container].iteritems():
            if self.root[index_name].has_key(v[index_field]):
                self.root[index_name][v[index_field]].insert(k)
            else:
                 self.root[index_name][v[index_field]] = OOTreeSet([k])
        #add index to index listing
        index_data = {index_field:[index_name,index_container,index_description]}
        self.root['index_listing'][index_container].insert= index_data
        #update object definintion
        self.root['object_definitions'][obj_name]['indexed_fields'][index_field] = index_name

    def checkConsistency(self,obj,fix_missing=False,remove_extra=False):
        """
        will check all objects in their assigned container for the required
        fields
        
        :param obj: the object to be checked
        :type obj: String
        :param fix_missing: if set to True correct the objects by adding the
                            value specified in the object definition
        :type fix_missing: Boolean
        :param remove_extra: if set to True the method will remove all fields
                             that are not in the object definition
        :type remove_extra: Boolean
        :returns: dict of objects that are/were not consistent with the object
                  definition

        """
        definition = self.root['object_definitions'][obj]
        records = {}
        x = 0
        for key,values in self.root[definition['container']].iteritems():
            issues ={}
            for k,v in values.iteritems():
                if not definition['definition'].has_key(k):
                    issues[k]='extra'                    
            for k,v in definition['definition'].iteritems():
                if not values.has_key(k):
                    issues[k]='missing'
            if issues:
                records[key]=issues
            x += 1
            if x % 5000 == 0 :
                print x
        if fix_missing or remove_extra:
            for k,v in records.iteritems():
                record = self.root[definition['container']][k]
                for j,w in v.iteritems():
                    if fix_missing and w == 'missing':
                        record[j] = definition['definition'][j]
                        print records[k][j]
                        records[k][j] = records[k][j] +': Fixed'
                    if remove_extra and w == 'extra':
                        record.pop(j)
                        records[k][j] = records[k][j] +': Fixed'
        return records

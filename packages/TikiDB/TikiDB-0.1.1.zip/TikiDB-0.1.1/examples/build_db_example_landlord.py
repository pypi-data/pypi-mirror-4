"""
This is an example of how to use the builder to create a ZODB that can be used
by TikiWare to create a web application.
This is a more complex example using more indexes for complex searches
"""
from tikidb.TikiDB import DB
from tikidb.TikiBuilder import Builder
import transaction
import os,re
from datetime import datetime
from time import time
#delete the example database so the example makes sense
if os.path.exists('slums.zodb'):
    os.remove('slums.zodb')
    for f in os.listdir('.'):
        if f.find('.zodb.')>-1:
            os.remove(f)

#create the db and make the builder available
db = DB('slums.zodb')
builder = Builder(db)

#create the containers
builder.create_container('people')#people who are in the db. owners and tennents
builder.create_container('building')#a building that has data.  has an address and people living there as well as an owner
builder.create_container('addresses')#addresses of people and buildings

#create the object definitions
person_obj ={'first_name':'','last_name':'','email':'','telephone':'',
             'address_obj':'','notes':[]
             }     #note that the tag_list has a value of list
                               #this is used to ensure that a list value is
                               #passed to the recipe as there can be many
                               #tags per recipe!

builder.create_object_definition('person','people',
                                 person_obj,'A person',0.1,
                                 datetime.now())

address_obj = {'address':'','city':'','state':'','zipcode':'','notes':[]}
builder.create_object_definition('address','addresses',address_obj,
                                 'An address',0.1,datetime.now())
#add people from a file
f = open('example_people.txt','r')
x = 0
for l in f:
    x +=1
    #print x
    s = re.sub(' +',' ',l)
    s = s.split('\t')
    person_obj={'first_name':s[0],'last_name':s[1][:-1],'email':'','telephone':'',
             'address_obj':'','notes':[]}
    err = db.create_object('person',person_obj)
    if x % 5000 == 0:
        transaction.savepoint()
        print x
transaction.commit()
f.close()
print 'build addresses'
#add addresses from file
x = 0
f = open('example_addresses.txt.','r')
for l in f:
    x +=1
    s = re.sub(' +',' ',l)
    s = s.split('\t')
    address_obj ={'address':s[0],'city':s[1],'state':s[2],'zipcode':s[3][:-1]
                  ,'notes':[]}
    err = db.create_object('address',address_obj)
    if x % 5000==0:
        transaction.savepoint()
        print x
                                 
#internal index of last name and first name
db.makeIndex('last_name_to_person','OOBTree','people','last_name','index of people with the same last name')
transaction.commit()

#find all people with the last name of JONES
stime = time()
people_id = db.root['index_last_name_to_person']['JONES']
people_count =0
for i in people_id:
    #print dict(db.root['people'][i])
    people_count += 1
    
print 'people with the last name JONES', people_count
t =time()-stime
print 'took %s seconds'%t

#find all the people with a last name starting with J
stime = time()
people_keys = db.root['index_last_name_to_person'].keys('J','J~')
people_count = 0                                                
for key in people_keys:
    people_id = db.root['index_last_name_to_person'][key]
    for k in people_id:
        people_count +=1
print 'total people found with last name starting with J', people_count
t =time()-stime
print 'took %s seconds'%t

#do search without index on last name
stime= time()
r = db.findObjectIdByField('person',[{'last_name':'JONES'}])
print 'total number of last name = jones: ',len(r)
t =time()-stime
print 'took %s seconds'%t
stime = time()
r = db.findObjectIdByField('person',[{'last_name':'J%'}])
print 'all names staring with J: ',len(r)
t =time()-stime
print 'took %s seconds'%t
#add a value to a list in a person then search for it
person = db.root['people'][1]
person['notes'].append('Owner')
transaction.commit()
r = db.findObjectIdByField('person',[{'notes':'Owner'}])
person = db.root['people'][r[0]]
print person," is an Onwer!"

#get the actual data
people =[]
for i in r:
    people.append(db.root['people'][i])

#sort the data by last name then first name in reverse by inline lambda
people.sort(key=lambda k:(k['last_name'],k['first_name']),reverse=True)
print people[0]
print people[len(people)-1]
print
print '----------------------------'

#resort data by firstname then lastname in accending order using db.sortData
p = db.sortData(people,['first_name','last_name'],'desc')
print people[0]
print people[len(people)-1]

#assign an address to a person and check
person = db.root['people'][6881]
address = db.root['addresses'][1]
person['address_obj'] = address
transaction.commit()
elk_people = db.findObjectIdByField('person',[{'address_obj':''},{'city':'ELK MOUND'}])
#loop through people and assisgn address based on key of person
x = 0
addresses = dict(db.root['addresses'])

for k,v in db.root['people'].iteritems():
    try:
        addr_key = addresses.iterkeys().next()
    except:
        addresses = dict(db.root['addresses'])
        addr_key = addresses.iterkeys().next()
    v['address_obj']= addresses.pop(addr_key)
    x += 1
    if x % 1000 == 0:
        transaction.savepoint()
        print x
print x
transaction.commit()
#clean up database
db.pack(t=None,days=2)
transaction.commit()
#check db for consistency
def_ok =db.checkConsistency('person')
#there should be no issues 
print 'total issues =',len(def_ok)
#lets make a couple of issues
person = db.root['people'][1]
person.pop('first_name')
person = db.root['people'][2]
person['extra_field'] ='I am Extra!!!'
transaction.commit()
#check db for consistency
def_ok =db.checkConsistency('person')
#there should be 2 issues, one extra on missing
print 'total issues =',len(def_ok)
print def_ok
#lets fix the errors. be sure you want to remove extra fields
#as this could delete data you want
def_ok =db.checkConsistency('person',fix_missing=True, remove_extra=True)
#should note there were 2 issues but they are fixed
print 'total issues =',len(def_ok)
print def_ok
#let's make sure
def_ok =db.checkConsistency('person',fix_missing=True, remove_extra=True)
print 'total issues =',len(def_ok)


#db.close()

from tikidb.TikiDB import DB
from tikidb.TikiBuilder import Builder
from datetime import datetime 
import transaction

db = DB('test.zodb')
builder = Builder(db)
#create a data conatiner
builder.create_container('muffins')
#create the object definition for the container
builder.create_object_definition('muffin','muffins',{'name':'','health_rating':'','rating_stars':''},"a muffin object",1.0,datetime.now())
#add objects
db.create_object('muffin',{'name':'basic','health_rating':'poor','rating_stars':'2'})
db.create_object('muffin',{'name':'blueberry','health_rating':'good','rating_stars':'4'})
db.create_object('muffin',{'name':'banana nut','health_rating':'average','rating_stars':'3'})
db.create_object('muffin',{'name':'heath topping','health_rating':'very poor','rating_stars':'5'})
db.create_object('muffin',{'name':'bran','health_rating':'excellent','rating_stars':'1'})
db.create_object('muffin',{'name':'strawberry','health_rating':'good','rating_stars':'4'})
#create an index using a string as the key value, any object other than integer use OOBTree 
db.makeIndex('health_of_muffin','OOBTree','muffins','health_rating','index of muffins that have the same health rating')
print 'Muffins with a good health_rating'
muffin_ids = list(db.root['index_health_of_muffin']['good'])
for muffin in muffin_ids:
    print db.root['muffins'][muffin]

muffin_ids= db.findObjectIdByField('muffin',[{'name':'b%'}])
print 'Muffins that start with b'
for muffin in muffin_ids:
    print db.root['muffins'][muffin]

muffin_ids= db.findObjectIdByField('muffin',[{'name':'%r%'}])
print 'Muffins that conatin the letter r'
for muffin in muffin_ids:
    print db.root['muffins'][muffin]

#commit the data or it will be lost
transaction.commit()
db.close()

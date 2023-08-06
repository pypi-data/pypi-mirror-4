"""
This is an example of how to use the builder to create a ZODB that can be used
by TikiWare to create a web application.
The example creates a recipe database that organizes recipies by tags.  It also
attributes the recipe to a person.

"""
from tikidb.TikiDB import DB
from tikidb.TikiBuilder import Builder
import transaction
import os
from datetime import datetime
#delete the example database so the example makes sense
if os.path.exists('recipes.zodb'):
    os.remove('recipes.zodb')
    for f in os.listdir('.'):
        if f.find('.zodb.')>-1:
            os.remove(f)


#create the database connection using tikiDB.DB().  the parameter is the file
#name of the database and must be a string that is a valid file name or path
#with a file name
db = DB('recipes.zodb')
#the builder is used to create the zodb database.  When instantiated it ensures
#that the base data containers are available
builder = Builder(db)
#list the default containers
print "this is a list of the default needed data containers:"
for i in db.root.keys():
    print '\t',i
#create the containers
builder.create_container('recipes')#house recipe data
builder.create_container('cookz')#house data about the cook who made the recipe
builder.create_container('tags')#tags that can be used
#I added the wrong container name. delete and recreate
err = db.root.pop('cooks',"does not exist")
#oops, the container to be removed is 'cookz' 
if err:
    print err
#lets make sure it deleted
err = db.root.pop('cookz',"does not exist") 
if err:
    print err
#ok we are good to go lets recreate it and look at the root objects
builder.create_container('cooks')
print db.root.keys()
#create the recipe object definition
#first make the fields in a dict
recipe_obj ={'recipe_name':'','recipe_ingredients':{},'recipe_directions':'',
            'tag_list':[],'cook':''
             }     #note that the tag_list has a value of list
                               #this is used to ensure that a list value is
                               #passed to the recipe as there can be many
                               #tags per recipe!

builder.create_object_definition('recipe','recipes',
                                 recipe_obj,'A tasty recipe!',0.1,
                                 str(datetime.now()))
#create the cooks and tags object
cook_obj ={'cook_name':'','email':''}
builder.create_object_definition('cook','cooks',cook_obj,
                                 'A person who is a cook',0.1,
                                 str(datetime.now()))
builder.create_object_definition('tag','tags',{'tag_name':''},
                                 'A tag to organize recipes',0.1,
                                 str(datetime.now()))
#lets add some data using the db interface
cook ={'cook_name':'Bobby Flay','email':'bobby.flay@food.net'}
db.create_object('cook',cook)
cook = {'cook_name':'Mr Food','email':'mrfood@gmail.com'}
db.create_object('cook',cook)
cook = {'cook_name':'Grahm Kerr','email':'gkerr@hotmail.com'}
db.create_object('cook',cook)
#lets look at the resultsmrfood@gmail.com
print dict(db.root['cooks'])
#add a cook not using a good object, raises error
cook ={'name':'The Swedish Chef','email':'borkbork.bork.com'}
z = db.create_object('cook',cook)
#now a recipe
recipe = {'recipe_name':'Tasty Cookies',
          'recipe_ingredients':{'Flour':'2 cups','Eggs':'1','Sugar':'1 cup',
                                'Butter':'1/2 cup','Baking soda':'1 Tbsp'},
          'recipe_directions':'throw ingrediants into bowl, mix then cook',
          'tag_list':[],'cook':db.root['cooks'][1]}
db.create_object('recipe',recipe)
#oops added wrong cook
cook = db.root['cooks'][2]
db.root['recipes'][1]['cook']=cook
#lets take a look at the receipe
recipe = db.root['recipes'][1]
print recipe
#hmm the cook's email is wrong!  lets change it here and see if it changes
#the cook object in the cooks container and updates the email in the receipe 
recipe['cook']['email']='mrfood@yummytumtum.com'
print 'cook is now',dict(db.root['cooks'][2])
print 'recipe is now',dict(db.root['recipes'][1])
#lets commit the data and then check our work again
transaction.commit()
db.close()
db = DB('recipes.zodb')
print 'is it there?', dict(db.root['recipes'][1])
print
print 'is the email changed?', db.root['recipes'][1]['cook']['email'], 'Yep!!!!'
#lets add more recipes!
recipe = {'recipe_name':'Air Cookies',
          'recipe_ingredients':{'Air':'1 liter'},
          'recipe_directions':'great for pretend tea!',
          'tag_list':[],'cook':db.root['cooks'][1]}
db.create_object('recipe',recipe)
recipe = {'recipe_name':'Roast Beast',
          'recipe_ingredients':{'Beast':'1','Salt':'2 Tbs'},
          'recipe_directions':'better than lappam',
          'tag_list':[],'cook':db.root['cooks'][3]}
db.create_object('recipe',recipe)
recipe = {'recipe_name':'water',
          'recipe_ingredients':{'water':'1 cup'},
          'recipe_directions':'put 1 cup of water into a cup',
          'tag_list':[],'cook':db.root['cooks'][3]}
db.create_object('recipe',recipe)
transaction.commit()
#need some tags
db.create_object('tag',{'tag_name':'desert'})
db.create_object('tag',{'tag_name':'drinks'})
db.create_object('tag',{'tag_name':'main course'})
#add tags to recipes
db.root['recipes'][1]['tag_list'].append(db.root['tags'][1])
db.root['recipes'][2]['tag_list'].append(db.root['tags'][1])
db.root['recipes'][3]['tag_list'].append(db.root['tags'][3])
db.root['recipes'][4]['tag_list'].append(db.root['tags'][2])

#make a tag index
db.makeIndex('tag_to_recipe','OOBTree','recipes','tag_list',
             'index of all recipes that have the specific tag')
#make a cook to receipe index
db.makeIndex('cook_to_recipe','OOBTree','recipes','cook','index of all recipes that a cook has created')

#lets find all the recipes that Grahm Kerr has created
#for this example we will iterate through all the cooks and find the name
for k,v in db.root['cooks'].iteritems():
    if v['cook_name']=='Grahm Kerr':
        cook = db.root['cooks'][k]
        break
#now get the recipes using the index
recipe_ids = db.root['index_cook_to_recipe'][cook]
print list(recipe_ids)
print cook['cook_name'] +'has created the following recipes'
for r in recipe_ids:
	print '\t'+ db.root['recipes'][r]['recipe_name']

    


#db.close()

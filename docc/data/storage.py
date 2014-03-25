"""
Storage interface
"""

import time
import traceback
from pymongo import Connection

class Storage(object):
    
    #Initialize db object to none
    db = None 
    
    def __init__(self):
       # initialize our storage, data is a placeholder
       self.data = {}
       # for demo
       self.data['created'] = time.ctime()
       connection = Connection('localhost', 27017)
       #Create db object only if it is not created 
       if self.db is None:
           self.db = connection.doccdb
    
    ####################################### Start############################################
    def add(self, collection, data):
        print 'In Storage.add method'
        try:
            print 'data added in doccdb'
            return self.db[collection].save(data)
            
        except:
            traceback.print_exc() 
            return "Error: Data cannot be added"
    
    def get(self, collection, fieldname, value):
        print 'In Storage.get method'
        try:
            return self.db[collection].find_one({fieldname:value}, {'_id':0})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
        
    def getInArray(self, collection, fieldname, values ):
        print 'In Storage.get method'
        try:
            return self.db[collection].find({fieldname:{'$in': values}})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
    
        
    def update(self, collection, fieldname, value, data):
        print 'In Storage.update method'
        try:
            self.db[collection].update({fieldname:value},{'$set': data});
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated"  
        
    def updateArray(self, collection, fieldname, value, data):
        print 'In Storage.update method'
        try:
            status = self.db[collection].update({fieldname:value},{'$addToSet': data});
            print status
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated"   
    
    def getAll(self, collection):
        print 'In Storage.getAll method'
        try:
            return self.db[collection].find() 
        except:
            traceback.print_exc() 
            return "All data cannot be retrieved" 
        
        
    
    ############################### End##############################################
    
    
    ############################ Extra functions #####################################
    
    
    
    def remove(self, collection, fieldname, value):
        print 'In Storage.remove method'
        try:
            self.db[collection].remove({fieldname:value})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be deleted"
    
    
    
    def enrollCourse(self, email, courseid):
        print 'In Storage.enrollCourse method'
        try:
            print email, courseid 
            self.db['user'].update({"email":email}, {'$push':{"enrolled":courseid}})
        except:
            traceback.print_exc() 
            return "Course cannot be enrolled"
    
    def dropCourse(self, email, courseid):
        print 'In Storage.dropCourse method'
        try:
            print email, courseid 
            self.db['user'].update({"email":email}, {'$pull':{"enrolled":courseid}})
        except:
            traceback.print_exc() 
            return "Course cannot be dropped"
    
    def addUserOwnCourse(self, email, courseid):
        print 'In Storage.addUserOwnCourse method'
        try:
            print email, courseid 
            self.db['user'].update({"email":email}, {'$push':{"own":courseid}})
        except:
            traceback.print_exc() 
            return "User own course cannot be updated"
    def insert(self,name,value):
       print "---> insert:",name,value
       try:
          self.data[name] = value
          return "added"
       except:
          return "error: data not added"
    
    def names(self):
       print "---> names:"
       for k in self.data.iterkeys():
         print 'key:',k
    
    def find(self,name):
       print "---> storage.find:",name
       print "Data values are", self.data
       if name in self.data:
          rtn = self.data[name]
          print "---> storage.find: got value",rtn
          return rtn
       else:
          return None
     



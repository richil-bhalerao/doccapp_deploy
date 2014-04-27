"""
Storage interface
"""

import time
import traceback
import pymongo
from pymongo import Connection
from random import randint

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
            return self.db[collection].find_one({fieldname:value})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
    
    def getCount(self, collection):
        print 'In Storage.get method'
        try:
            return self.db[collection].find().count()
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
    
    def getRankedUsers(self, collection):
        print 'In Storage.getranked users method'
        try:
            return self.db[collection].find().sort('StarsAchieved', pymongo.DESCENDING)
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
        
    def getRandomRecord(self, collection, fieldname, value):
        print 'In Storage.getRandomRecord'
        count = 0
        try:
            count = self.db[collection].find({fieldname:value}).count()
            print count
            return self.db[collection].find({fieldname:value}).limit(-1).skip(randint(1, count-1)).next()
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
    
    
    def getAllFiltered(self, collection, fieldname, value):
        print 'In Storage.get method'
        try:
            return self.db[collection].find({fieldname:value})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
        
    def getAllUsers(self, collection, data):
        print 'In Storage.getAllUsers method'
        try:
            return self.db[collection].find(data)
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"    
        
    def getInArray(self, collection, fieldname, values):
        print 'In Storage.getInArray method'
        try:
            return self.db[collection].find({fieldname:{'$in': values}})
        # Add a sort as per sub category in the above line
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
    
    def getArrayElementsMatched(self, collection, fieldname, value, arrayElem, data):
         print 'In Storage.getArrayElementsMatched method'
         try:
             return self.db[collection].find({fieldname:value}, {arrayElem:{'$elemMatch': data}})
        # Add a sort as per sub category in the above line
         except:
             traceback.print_exc() 
             return "Error: Data cannot be retrieved"
    
    def getAllArrayElements(self, collection, fieldname, value, projection):
        print 'In Storage.getAllArrayElements method'
        try:
            return self.db[collection].find({fieldname: value}, {projection:1})
        # Add a sort as per sub category in the above line
        except:
            traceback.print_exc() 
            return "Error: Data cannot be retrieved"
        
               
    def update(self, collection, fieldname, value, data):
        print 'In Storage.update method'
        try:
            self.db[collection].update({fieldname:value},{'$set': data})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated"  
    
    # Only used to update challenge.. Don't use this as a generic query method
    def updateChallenge(self, collection, username, usernameValue, category, questionId, booleanPlayedStatus, score, booleanResult, opponentUsername):
        print 'In Storage.update challenge method'
        try:
            self.db[collection].update({username:usernameValue, 'challenge.category':category},{'$set': {'challenge.$.opponentUsername':opponentUsername, 'challenge.$.poll_id': questionId, 'challenge.$.status': booleanPlayedStatus, 'challenge.$.score': score, 'challenge.$.won' : booleanResult}})
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated" 
    
    def updateArray(self, collection, fieldname, value, data):
        print 'In Storage.update Array method'
        print data
        try:
           status = self.db[collection].update({fieldname:value},{'$addToSet': data})
           print status
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated"
        
    def updateAndIncrement(self, collection, fieldname, value, data):
        print 'In Storage.update Array method'
        print data
        try:
           status = self.db[collection].update({fieldname:value},{'$inc': data})
           print status
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated"
        
    def updateArrayOneField(self, collection, searchCriteriaJson, data):
        print 'In Storage.update Array method'
        print data
        try:
           status = self.db[collection].update(searchCriteriaJson,{'$set': data})
           print status
        except:
            traceback.print_exc() 
            return "Error: Data cannot be updated"   
    
    def removeFromArray(self, username, contentId):
        print 'In Storage.removeFromArray method'
        try:
            self.db['user'].update({"username":username}, {'$pull':{"ContentId":contentId}})
        except:
            traceback.print_exc() 
            return "Content cannot be removed"
            
    def removeFromArrayOfJSON(self, collection, usernamevalue, arrayname, fieldname, fieldvalue):
    	print 'In Storage.remove from Array method'
        
        try:
           status = self.db[collection].update({"username":usernamevalue},{'$pull':{arrayname:{fieldname:fieldvalue}}})
           print status
        except:
            traceback.print_exc() 
            return "Error: Data cannot be removed"   
    	
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
     



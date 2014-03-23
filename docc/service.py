"""
6, Apr 2013
Last updated on 03/02/2014
"""

import time
import sys
import socket

# bottle framework
from bottle import request, response, route, run, template, abort


import traceback
from course import Course
from user import Users
from session import Session
from professor import Professors

import json
from inspect import trace
from bson.objectid import ObjectId
from json import JSONEncoder
from pymongo import *
from data.storage import Storage
from recoengine import RecoEngine

storageobj = None
sessionobj = None
status = None
recoObj = None


class MongoEncoder(JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return JSONEncoder.default(obj, **kwargs) 




##########################################Code clean up ############################################

# Displaying welcome 
@route('/')
def root():
    cookie = request.get_cookie("session")
    print 'cookie: ', cookie
    username = sessionobj.get_username(cookie)
    if username is None:
        return 'User not logged in'
    else:
        return 'Hi and Welcome: ', username

def setup():
   print '\n**** service initialization ****\n'
   global storageobj, sessionobj, recoObj
   storageobj = Storage()
   recoObj = RecoEngine()
   connection = Connection('localhost', 27017)
   sessionobj = Session(connection.doccdb) 

# User registration
@route('/register', method='POST')
def create_user(): 
    print 'Bottle: in create user'
    user=''
    entity = request.body.read()
    user = json.loads(entity)
    print user
    print '----'
    status = storageobj.add('user', user)
    print "----"
    print status
    return str(ObjectId(status))

# User sign In 
@route('/signIn', method='PUT')
def signIn():
    print 'Checking if user exists..'
    entity = request.body.read()
    entity = json.loads(entity)
    print "username:", entity['username']
    user = storageobj.get('user', 'username', entity['username'])
    print "user returned: ",  user
    if user!=None and user['password']==entity['password']:
        
        #Also set session id in the browser cookie
        session_id = sessionobj.start_session(user['username'] )
        response.set_cookie("session", session_id)
        data = user
        print 'username and pwd match'
    else:
        print 'incorrect pwd'
        data = {}
    return data

@route('/professorSignIn', method='PUT')
def professorSignIn():
    print 'Checking if user exists..'
    entity = request.body.read()
    entity = json.loads(entity)
    print "username:", entity['username']
    professor = storageobj.get('professor', 'username', entity['username'])
    print "professor returned: ",  professor
    if professor!=None and professor['password']==entity['password']:
        
        #Also set session id in the browser cookie
        session_id = sessionobj.start_session(professor['username'] )
        response.set_cookie("session", session_id)
        data = professor
    else:
        data = None
    
    return data

### RP: TO DO: Incomplete 
@route('/courseContentSelection', method='GET')
def courseContentSelection():
    print 'Bottle: you are in courseContentSelection'
    cursor = storageobj.getAll('content')
    entity = [d for d in cursor]
    print entity     
    return  entity

@route('/getProfile', method='PUT')
def get_user():
    print 'You are in get user service'
    username = ''
    entity = request.body.read()
    username = json.loads(entity)
    entity = storageobj.get('user', 'username', username['username'])
    print 'ENTITY ---> ', entity
    return entity


@route('/saveProfile', method='POST')
def saveProfile():
    print "In save profile"
    entity = request.body.read()
    user = json.loads(entity)
    print "PAYLOAD USER ---> ", user
    print "USERNAME ---> ", user['username']
    status = storageobj.updateArray('user', 'username', user['username'], user)
    print "STATUS ---> ", status
    return status


###########################################################################


#===================================Recommendation service==============================================

@route('/mostviewedcontent', method='PUT')
def getMostViewed():
    print 'you are in getMostViewed service'
    entity = request.body.read()
    data = json.loads(entity)
    #print 'DATA - > ' + data['sub_category']
    try:
        cursor = recoObj.getMostViewedContent(data['sub_category'])
        entity = [d for d in cursor]
        
    except:
        traceback.print_exc()
        abort(404, 'Most viewed cannot be retrieved')    
        
    if not entity:
        abort(404, 'No content found')       
        
    return MongoEncoder().encode(entity)


@route('/mostratedcontent', method='PUT')
def getMostRated():
    print 'you are in getmostratedViewed service'
    entity = request.body.read()
    data = json.loads(entity)
    try:
        cursor = recoObj.getMostRatedContent(data['sub_category'])
        entity = [d for d in cursor]
    except:
        traceback.print_exc()
        abort(404, 'Most viewed cannot be retrieved')    
        
    if not entity:
        abort(404, 'No content found')       
        
    return MongoEncoder().encode(entity)

@route('/wesuggest/:username', method='GET')
def getWeSuggest(username):
    print 'You are in get we suggest service'
    print username
    
    try:
        cursor = recoObj.getWeSuggest(username)
        entity = [d for d in cursor]
        print entity
    except:
        traceback.print_exc()
        abort(404, 'suggested content cannot be retrieved')    
        
    if not entity:
        abort(404, 'No content for recommendation')       
    
    
    
    return MongoEncoder().encode(entity)



#------------------------------------ @ Roopak - Adding the content to user's cart -----------------------------------#

@route('/viewAll', method='GET')
def getViewAll():
    print 'you are in getViewAll service'
    
    try:
        cursor = recoObj.getViewAllContent()
        entity = [d for d in cursor]
    except:
        traceback.print_exc()
        abort(404, 'Most viewed cannot be retrieved')    
        
    if not entity:
        abort(404, 'No content found')       
        
    return MongoEncoder().encode(entity)













@route('/addToCart', method='POST')
def addToCart():
    print "In Add to Cart "
    entity = request.body.read()
    payload = json.loads(entity)
    print "PAYLOAD USER ---> ", payload
    print "USERNAME ---> ", payload['username']
    print "CONTENT ID--->", payload['contentId']
    data = {"ContupdatentId": payload['contentId']}
    status = storageobj.updateArray('user', 'username', payload['username'], data)
    print "STATUS ---> ", status
    return status

#----------------------------------------------------------------------End --------------------------------------------------#

   
   




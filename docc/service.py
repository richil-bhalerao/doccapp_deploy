"""
6, Apr 2013
Last updated on 03/02/2014
"""

import time
import sys
import socket
import gridfs
# bottle framework
from bottle import request, response, route, run, template, abort


import traceback
from course import Course
from user import Users
from session import Session
from professor import Professors
from random import randint
import json
from inspect import trace
from bson.objectid import ObjectId
from json import JSONEncoder
from pymongo import *
from data.storage import Storage
from recoengine import RecoEngine
import gridfs

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
    
    username = sessionobj.get_username(cookie)
    if username is None:
        return 'User not logged in'
    else:
        return 'Hi and Welcome: ', username

def setup():
   global storageobj, sessionobj, recoObj
   storageobj = Storage()
   recoObj = RecoEngine()
   connection = Connection('localhost', 27017)
   sessionobj = Session(connection.doccdb) 
   

# User registration
@route('/register', method='POST')
def create_user(): 
    #print 'Bottle: in create user'
    user=''
    entity = request.body.read()
    user = json.loads(entity)
    if user['usertype'] == 'Professor':
        status = storageobj.add('professor', user['dbpayload'])
    else:
        status = storageobj.add('user', user['dbpayload'])
    
    
    return str(ObjectId(status))

# User sign In 
@route('/signIn', method='PUT')
def signIn():
    #print 'Checking if user exists..'
    entity = request.body.read()
    entity = json.loads(entity)
    #print "username:", entity['username']
    user = storageobj.get('user', 'username', entity['username'])
    #print "user returned: ",  user
    if user!=None and user['password']==entity['password']:
        
        #Also set session id in the browser cookie
        session_id = sessionobj.start_session(user['username'] )
        response.set_cookie("session", session_id)
        data = user
        #print 'username and pwd match'
    else:
        #print 'incorrect pwd'
        data = {}
    return MongoEncoder().encode(data)

@route('/professorSignIn', method='PUT')
def professorSignIn():
    #print 'Checking if user exists..'
    entity = request.body.read()
    entity = json.loads(entity)
    #print "username:", entity['username']
    professor = storageobj.get('professor', 'username', entity['username'])
    #print "professor returned: ",  professor
    if professor!=None and professor['password']==entity['password']:
        
        #Also set session id in the browser cookie
        session_id = sessionobj.start_session(professor['username'] )
        response.set_cookie("session", session_id)
        data = professor
    else:
        data = None
    
    return MongoEncoder().encode(data)

### RP: TO DO: Incomplete 
@route('/courseContentSelection', method='GET')
def courseContentSelection():
    print 'Bottle: you are in courseContentSelection'
    cursor = storageobj.getAll('content')
    entity = [d for d in cursor]
    print entity     
    return  MongoEncoder().encode(entity)

@route('/getProfile', method='PUT')
def get_user():
    print 'You are in get user service'
    username = ''
    entity = request.body.read()
    username = json.loads(entity)
    entity = storageobj.get('user', 'username', username['username'])
    print 'ENTITY ---> ', entity
    return MongoEncoder().encode(entity)

@route('/getAllUsersOfCategory', method='PUT')
def getAllUsersOfCategory():
    print 'You are in get all users of a category'
    entity = request.body.read()
    category = json.loads(entity)
    subcat = category['sub_category']
    print 'category:', subcat
    data = {}
    abc={'$lt':100}
    if subcat == "1.1" or subcat =="1.2":
        print 'in category 1'
        data = {'CategoryOnePercentage': abc }
    if subcat == "2.1" or subcat =="2.2":
        data = {'CategoryTwoPercentage': abc }
    if subcat == "3.1" or subcat =="3.2":
        data = {'CategoryThreePercentage': abc }
    if subcat == "4.1" or subcat =="4.2":
        data = {'CategoryFourPercentage': abc }
    if subcat == "5.1" or subcat =="5.2":
        data = {'CategoryFivePercentage': abc }
    
    
    print 'data-->', data
    entity = storageobj.getAllUsers('user', data)
#     for i in entity:
#         print 'ENTITY ---> ', i
    AllUsers = [e for e in entity]
    print 'All Users of Catgeory', AllUsers
    return MongoEncoder().encode(AllUsers)

@route('/saveProfile', method='PUT')
def saveProfile():
    print "In save profile"
    entity = request.body.read()
    user = json.loads(entity)
    print "PAYLOAD USER ---> ", user
    print "USERNAME ---> ", user['username']
    data = {"CategoryOnePercentage":user['CategoryOnePercentage'],"CategoryTwoPercentage":user['CategoryTwoPercentage'],"CategoryThreePercentage":user['CategoryThreePercentage'],"CategoryFourPercentage":user['CategoryFourPercentage'],"CategoryFivePercentage":user['CategoryFivePercentage'], }
    status = storageobj.update('user', 'username', user['username'], data)
    print "STATUS ---> ", status
    return MongoEncoder().encode(status)


###########################################################################


#===================================Recommendation service==============================================

@route('/mostviewedcontent', method='PUT')
def getMostViewed():
    print 'you are in getMostViewed service'
    entity = request.body.read()
    data = json.loads(entity)
    print 'DATA - > ' + data['sub_category']
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

@route('/wesuggest/', method='GET')
def getWeSuggest():
    print 'You are in get we suggest service'
    username = request.body.read()
    
    print username
    user = json.loads(username)
    print user['username']
    print user['sub_category']
    try:
        cursor = recoObj.getWeSuggest(user['username'])
        entity = [d for d in cursor]
        print "Recommendation Output: "
        
        list1 = []
        list2 = []
        data = []
        
        
        for e in entity:
            print e[0], ":", e[1]
            list1.append(e[0])
            list2.append(e[1])
        
        print "List1: "
        print list1
       
        list3 = []
        print "List2: "
        for l in list2:
            for innerItem in l:
                list3.append(innerItem)
                
        contents = storageobj.getInArray('content', '_id', list3)
        #jsonData["Similarity"].append(list1)
        #jsonData["CourseId"].append(list2)
        print 'Content-->'
       
        
       
        #values = [d for d in contents]
        
        #print 'values-->'
        #print values
        
        print "Recommended Content:"
        
        for v in contents: 
            print 'v values: '
            print v
            print v['sub_category']
            if v['sub_category'] == user['sub_category']:
                print 'in if'
                data.append(v)
        
        print 'DATA-->',data           

    except:
        traceback.print_exc()
        abort(404, 'suggested content cannot be retrieved')    
        
    if not entity:
        abort(404, 'No content for recommendation')       
    
  #  print  MongoEncoder().encode(entity)
    if not data:
        print 'in data is empty'
        data = []
        print 'DATA', data

    return MongoEncoder().encode(data)




#------------------------------------ @ Roopak - Adding the content to user's cart -----------------------------------#

@route('/viewAll', method='PUT')
def getViewAll():
    print 'you are in getViewAll service'
    entity = request.body.read()
    data = json.loads(entity)
    try:
        cursor = recoObj.getViewAllContent(data['sub_category'])
        entity = [d for d in cursor]
    except:
        traceback.print_exc()
        abort(404, 'Most viewed cannot be retrieved')    
        
    if not entity:
        abort(404, 'No content found')       
        
    return MongoEncoder().encode(entity)

@route('/addToCart', method='POST')
def addToCart():
    print "In Add to Cart"
    entity = request.body.read()
    payload = json.loads(entity)
    print "PAYLOAD USER ---> ", payload
    print "USERNAME ---> ", payload['username']
    print "CONTENT ID--->", payload['contentId']
    
    contentCompleted = {"sub_category":payload['sub_category'],"ChallengeQuestions":[], "ContentId":ObjectId(payload['contentId']), "ChallengeTaken":0, "ContentCompletedPercentage":20, "QuizTaken":0}
    data = {"ContentId": ObjectId(payload['contentId']), "contentCompleted":contentCompleted}
    status = storageobj.updateArray('user', 'username', payload['username'], data)
    print "STATUS ---> ", status
    return status
    
@route('/removeFromCart', method='POST')
def removeFromCart():
	print 'In remove from cart method'
	entity = request.body.read()
	payload = json.loads(entity)
	print 'PAYLOAD REMOVE CONTENT -> ', payload
	status1 = storageobj.removeFromArray(payload['username'], ObjectId(payload['ContentId']))
	#collection,  usernamevalue, arrayname, fieldname, fieldvalue
	status = storageobj.removeFromArrayOfJSON('user', payload['username'], 'contentCompleted', 'ContentId', ObjectId(payload['ContentId']))
	return status

@route('/uploadContent', method='POST')
def uploadContent():
    print "In Upload Content"
    entity = request.body.read()
    payload = json.loads(entity)
    print "PAYLOAD USER ---> ", payload
    status = storageobj.add('content', payload)
    print "----"
    print status
    return str(ObjectId(status))
    
@route('/getUserContent', method='GET')
def get_user_Content():
    print 'You are in get user content'
    username = ''
    entity = request.body.read()
    username = json.loads(entity)
    user = storageobj.get('user', 'username', username['username'])
    print 'USER ---> ', user
    print user['ContentId']
    content = storageobj.getInArray('content', '_id', user['ContentId'])
    print content
    contents = [c for c in content]
    print contents
    return MongoEncoder().encode(contents)

@route('/getRankedUsers', method='GET')
def getRankedUsers():
    print 'get all ranked users'
    rankedUsers = storageobj.getRankedUsers('user')
    print rankedUsers
    rankedUsers1 = [c for c in rankedUsers]
    return MongoEncoder().encode(rankedUsers1)

@route('/getProfessorContent', method='GET')
def get_professor_Content():
    print 'You are in get user content'
    username = ''
    entity = request.body.read()
    username = json.loads(entity)
    content = storageobj.getAllFiltered('content', 'prof_username', username['username'])
    print content
    contents = [c for c in content]
    print contents
    return MongoEncoder().encode(contents)


@route('/getCurrentContent', method='PUT')
def get_current_content():
    print 'You are in get current content'
    entity = request.body.read()
    print entity
    contentId = json.loads(entity)['contentId']
    if contentId=="":
        contentId='FirstTimeNoCurrentContent'
        print contentId
        content = {'sub_category':contentId}
    else:
        username = json.loads(entity)['username']
        content = storageobj.get('content', '_id', ObjectId(contentId) )
        #------------- Code to update the current content--------------------------------------#
        print 'Update current content'
        userJson = storageobj.get('user', 'username', username)
        listOfSubCategory = [ ]
        print 'User-->', userJson
        for i in userJson['contentCompleted']:
            
            print 'contentCompleted list'
            subcat = i['sub_category']
            listOfSubCategory.append(float(subcat))
            #listOfSubCategory.append[i['sub_category']]
        
        sortedListOfSubCategory = sorted(listOfSubCategory)
        print 'Sorted: ', sortedListOfSubCategory
        flag = False
        data = {}
        for i in sortedListOfSubCategory: 
            print 'i: ', i
            for j in userJson['contentCompleted']:
                print 'j', j
                subCatString = i
                print 'i value of sub cat', i
                print 'float value of Sub Cat ', float(j['sub_category'])
                if i == float(j['sub_category']) and j['ContentCompletedPercentage']!=100:
                    print 'current Sub Category', j['sub_category']
                    print 'Current content', j['ContentId']
                    data={"currentContent":j['ContentId']}
                    flag = True
                    
            if flag:
                break;

        print 'data-->',data
        status = storageobj.update('user', 'username', username,data)
        print 'content ---> ', content
    
    return MongoEncoder().encode(content)

@route('/updateAndIncNoOfPeopleRated', method='PUT')
def updateAndIncNoOfPeopleRated():
    print 'You are in update content'
    entity = request.body.read()
    contentId = json.loads(entity)['id']
    print contentId
    data={"NoOfPeopleRated":1}
    content = storageobj.updateAndIncrement('content', '_id', ObjectId(contentId), data)
    print 'content ---> ', content
    return MongoEncoder().encode(content)

@route('/updateAverageRating', method='PUT')
def updateAverageRating():
    print 'You are in update Average Rating'
    entity = json.loads(request.body.read())
    contentId = entity['id']
    AverageRating = int(entity['AverageRating'])
    print contentId
    print AverageRating
    data={'AverageRating':AverageRating}
    content = storageobj.update('content', '_id', ObjectId(contentId), data)
    print 'content ---> ', content
    return MongoEncoder().encode(content)

@route('/getContent', method='PUT')
def get_content():
    print 'You are in get  content'
    entity = request.body.read()
    contentId = json.loads(entity)['id']
    print contentId
    content = storageobj.get('content', '_id', ObjectId(contentId) )
    print 'content ---> ', content
    return MongoEncoder().encode(content)

@route('/getCount', method='GET')
def get_count():
    print 'You are in get  all content count'
    #entity = request.body.read()
    #contentId = json.loads(entity)['id']
    #print contentId
    contentcount = storageobj.getCount('content')
    print 'content count---> ', contentcount
    return MongoEncoder().encode(contentcount)



@route('/uploadQuiz', method='POST')
def uploadQuiz():
    print "In Upload Quiz"
    entity = request.body.read()
    payload = json.loads(entity)
    
    for q in payload['payload']['Questions']:
        print 'result:', q
        finalPayload = {"Questions": q} 
        status = storageobj.updateArray('content', 'Name', payload['Name'], finalPayload)
        
        
    return str(ObjectId(status))


#------------------------------------------------ Gamification API ---------------------------------------------------------------# 

@route('/getCategoryCompletedPercentage', method = 'PUT')
def getCategoryCompletedPercentage():
    print 'in get category completed percentage'
    payload = json.loads(request.body.read()) 
    contentCompleted = storageobj.getAllArrayElements('user', 'username', payload['username'], 'contentCompleted')
    courseCompletedPercentage = 0
    CategoryOnePercentage=CategoryTwoPercentage=CategoryThreePercentage=CategoryFourPercentage=CategoryFivePercentage=0
    SubCategory11=SubCategory12=SubCategory21=SubCategory22=SubCategory31=SubCategory32=SubCategory41=SubCategory42=SubCategory51=SubCategory52=0
    
    for contents in contentCompleted:
        print 'CONTENTS IN FOR -- ', contents
        if 'contentCompleted' in contents:
            for content in contents['contentCompleted']: 
                print content
                if content['sub_category']=="1.1":
                    if SubCategory11<= content['ContentCompletedPercentage']:
                        SubCategory11 = content['ContentCompletedPercentage']
                        print SubCategory11
                if content['sub_category']=="1.2":
                    if SubCategory12<= content['ContentCompletedPercentage']:
                        SubCategory12 = content['ContentCompletedPercentage']  
                        print SubCategory12
                if content['sub_category']=="2.1":
                    if SubCategory21<= content['ContentCompletedPercentage']:
                        SubCategory21 = content['ContentCompletedPercentage']
                        print SubCategory21
                if content['sub_category']=="2.2":
                    if SubCategory22<= content['ContentCompletedPercentage']:
                        SubCategory22 = content['ContentCompletedPercentage']  
                        print SubCategory22
                if content['sub_category']=="3.1":
                    if SubCategory31<= content['ContentCompletedPercentage']:
                        SubCategory31 = content['ContentCompletedPercentage']
                        print SubCategory31
                if content['sub_category']=="3.2":
                    if SubCategory32<= content['ContentCompletedPercentage']:
                        SubCategory32 = content['ContentCompletedPercentage']  
                        print SubCategory32
                if content['sub_category']=="4.1":
                    if SubCategory41<= content['ContentCompletedPercentage']:
                        SubCategory41 = content['ContentCompletedPercentage']
                        print SubCategory41
                if content['sub_category']=="4.2":
                    if SubCategory42<= content['ContentCompletedPercentage']:
                        SubCategory42 = content['ContentCompletedPercentage']  
                        print SubCategory42
                if content['sub_category']=="5.1":
                    if SubCategory51<= content['ContentCompletedPercentage']:
                        SubCategory51 = content['ContentCompletedPercentage']
                        print SubCategory51
                if content['sub_category']=="5.2":
                    if SubCategory52<= content['ContentCompletedPercentage']:
                        SubCategory52 = content['ContentCompletedPercentage']  
                        print SubCategory52
    CategoryOnePercentage = (SubCategory11 + SubCategory12)/2
    CategoryTwoPercentage = (SubCategory21 + SubCategory22)/2
    CategoryThreePercentage = (SubCategory31 + SubCategory32)/2
    CategoryFourPercentage = (SubCategory41 + SubCategory42)/2
    CategoryFivePercentage = (SubCategory51 + SubCategory52)/2
    
    courseCompletedPercentage = (CategoryOnePercentage+CategoryTwoPercentage+CategoryThreePercentage+CategoryFourPercentage+CategoryFivePercentage)/5
    return {'CourseCompletedPercentage':courseCompletedPercentage, 'CategoryOnePercentage':CategoryOnePercentage, 'CategoryTwoPercentage':CategoryTwoPercentage, 'CategoryThreePercentage':CategoryThreePercentage, 'CategoryFourPercentage':CategoryFourPercentage, 'CategoryFivePercentage':CategoryFivePercentage}

# @route('/getSubCatCompleted', method = 'PUT')
# def getConentCompleted():
#     print 'in get sub cat Completed - getting array'
#     payload = json.loads(request.body.read()) # get username, sub cat, contentID 
#     data = {'sub_category':payload['sub_category'], 'ContentCompletedPercentage':100, 'ContentId':ObjectId(payload['contentId'])}
#     contentCompleted = storageobj.getArrayElementsMatched('user', 'username', payload['username'], 'contentCompleted', data )
#     print contentCompleted 
#     return contentCompleted

@route('/updateContentCompleted', method='PUT')
def updateContentCompleted():
    print 'in update content completed Percentage'
    payload = json.loads(request.body.read()) # username and content id and sub category 
    #contentCompleted = {"sub_category":payload['sub_category'],"ChallengeQuestions":[], "ContentId":ObjectId(payload['contentId']), "ChallengeTaken":payload['ChallengeTaken'], "ContentCompletedPercentage":payload['ContentCompletedPercentage'], "QuizTaken":payload['QuizTaken']}
   
    searchCriteriaJson = {'username':payload['username'], "contentCompleted.ContentId": ObjectId(payload['contentId'])}
    print 'Search Criteria--->', searchCriteriaJson
    data = {"contentCompleted.$.ContentCompletedPercentage":payload['ContentCompletedPercentage']}
    print 'DATA--->', data
    status = storageobj.updateArrayOneField('user',searchCriteriaJson, data)
    print "STATUS ---> ", status
    return status

@route('/getCourseCompletedPercentage', method='PUT')
def getCourseCompletedPercentage():
    print 'in get course completed percentage'
    payload = json.loads(request.body.read()) # get username 
    status = storageobj.get('user', 'username', payload['username'])
    print status.json()
    CourseCompletedPercentage = {'CourseCompletedPercentage': status.json()['CourseCompletedPercentage']}
    print CourseCompletedPercentage
    if CourseCompletedPercentage==None:
        CourseCompletedPercentage=0
    return CourseCompletedPercentage

# @route('/updateCourseCompletedPercentage', method='PUT')
# def updateCourseCompletedPercentage():
#     print 'in update course completed percentage'
#     payload = json.loads(request.body.read()) # get username, courseCompletedPercentage value 
#     data = {'CourseCompletedPercentage': payload['courseCompletedPercentage']}
#     status = storageobj.update('user', 'username', payload['username'], data)
#     print status.json()
#     return status

@route('/getRandomPoll', method='PUT')
def getRandomPoll():
    print 'in get Random Poll'
    entity = json.loads(request.body.read())
    randomQuestion = storageobj.getRandomRecord('gameQuestions', 'sub_category', entity['sub_category'])
    return MongoEncoder().encode(randomQuestion)

@route('/getSpecificPollQuestion', method='PUT')
def getSpecificPollQuestion():
    print 'in get Specific Poll'
    entity = json.loads(request.body.read())
    print entity['pollQuestionId']
    specificQuestion = storageobj.get('gameQuestions', '_id', ObjectId(entity['pollQuestionId']))
    print "Question", specificQuestion
    return MongoEncoder().encode(specificQuestion)

@route('/updatePolledQuestion', method='PUT')
def updatePollQuestion():
    print 'in update poll question'
    entity = json.loads(request.body.read())
    searchCriteria = {"_id":ObjectId(entity['pollQuestionId']), "answers.optionId":entity['optionId']}
    data = {"answers.$.count":entity['count']}
    updateQuestion = storageobj.updateArrayOneField('gameQuestions', searchCriteria, data)
    return MongoEncoder().encode(updateQuestion)

@route('/incStars', method='PUT')
def updateAndIncrementStars():
    print 'in update and inc stars'
    entity = json.loads(request.body.read())
    data={'StarsAchieved': entity['incValue']}
    print 'stars data', data
    status = storageobj.updateAndIncrement('user', 'username', entity['username'], data )
    print status 
    return MongoEncoder().encode(status)

@route('/incStars', method='PUT')
def updateAndIncrementStars():
    print 'in update and inc stars'
    entity = json.loads(request.body.read())
    data={'StarsAchieved': entity['incValue']}
    print 'stars data', data
    status = storageobj.updateAndIncrement('user', 'username', entity['username'], data )
    print status 
    return MongoEncoder().encode(status)

@route('/incContentCount', method='PUT')
def updateAndIncContentCount():
    print 'in update and inc content count'
    entity = json.loads(request.body.read()) # send content Id
    data={'count': 1}
    print 'content view count', data
    status = storageobj.updateAndIncrement('content', '_id', ObjectId(entity['contentId']), data )
    print status 
    return MongoEncoder().encode(status)

@route('/updateAndAddRatingCount', method='PUT')
def updateAndAddRatingCount():
    print 'in update and add rating count'
    entity = json.loads(request.body.read()) # send content Id and present rating
    data={'RatingCount':int(entity['RatingCount'])}
    print 'Rating Count', data
    print 'ContentId', ObjectId(entity['id'])
    status = storageobj.updateAndIncrement('content', '_id', ObjectId(entity['id']), data )
    print status 
    
    return MongoEncoder().encode(status)


@route('/getQuiz/:id', method = 'GET')
def getQuiz(id):
    print "In get quiz"
    try:
        entity = storageobj.get('content', '_id', ObjectId(id))
        questions = entity['Questions']
    except:
        traceback.print_exc()
        

    return MongoEncoder().encode(questions)

@route('/submitQuizGrade', method = 'POST')
def submitQuizGrade():
    print 'you are in submit quiz grade service'
    try:
        payload = json.loads(request.body.read())
        
        quiz_scores = {"quiz_scores": payload['data']}
        username = payload['username']
        
        storageobj.updateArray('user', 'username', username, quiz_scores)
    except:
        traceback.print_exc()
        
@route('/playFeud', method = 'PUT')
def playFeud():
    print 'you are in play feud service'
    entity = json.loads(request.body.read())
    randomQuestion = ''
    category = ''
    if entity['sub_category'] == '1.1' or entity['sub_category']== '1.2':
    	category = 'category1'
    	randomQuestion1 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '1.1')
    	randomQuestion2 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '1.2')	
    	if randint(1,2) == 1:
    		randomQuestion = randomQuestion1
    	else:
    		randomQuestion = randomQuestion2
    if entity['sub_category'] == '2.1' or entity['sub_category']== '2.2':
    	category = 'category2'
    	randomQuestion1 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '2.1')
    	randomQuestion2 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '2.2')	
    	print 'RANDOMQUSTION 1 ---> ', randomQuestion1
    	print 'RANDOMQUSTION 2 ---> ', randomQuestion2
    	if randint(1,2) == 1:
    		randomQuestion = randomQuestion1
    	else:
    		randomQuestion = randomQuestion2
    	print 'FINAL RANDOM QUESTION --> ', randomQuestion
    if entity['sub_category'] == '3.1' or entity['sub_category']== '3.2':
    	category = 'category3'
    	randomQuestion1 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '3.1')
    	randomQuestion2 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '3.2')	
    	if randint(1,2) == 1:
    		randomQuestion = randomQuestion1
    	else:
    		randomQuestion = randomQuestion2
    if entity['sub_category'] == '4.1' or entity['sub_category']== '4.2':
    	category = 'category4'
    	randomQuestion1 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '4.1')
    	randomQuestion2 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '4.2')	
    	if randint(1,2) == 1:
    		randomQuestion = randomQuestion1
    	else:
    		randomQuestion = randomQuestion2
    if entity['sub_category'] == '5.1' or entity['sub_category']== '5.2':
    	category = 'category5'
    	randomQuestion1 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '5.1')
    	randomQuestion2 = storageobj.getRandomRecord('gameQuestions', 'sub_category', '5.2')	
    	if randint(1,2) == 1:
    		randomQuestion = randomQuestion1
    	else:
    		randomQuestion = randomQuestion2
    status1 = storageobj.updateChallenge('user', 'username', entity['opponentUsername'], category, randomQuestion['_id'], 0, 0, 0, entity['username'])
    status2 = storageobj.updateChallenge('user', 'username', entity['username'], category, randomQuestion['_id'], 0, 0, 0, entity['opponentUsername'])
    print status
    return MongoEncoder().encode(status1)


#Ric Start
@route('/endGame', method = 'POST')
def endGame():
    print 'you are in end game service'
    try:
        payload = json.loads(request.body.read())
        username = payload['username']
        pollId = payload['pollId']
        score = int(payload['score'])
        opponent = payload['opponent']
        
        searchCriteria = {"username":username, "challenge.poll_id":ObjectId(pollId)}
        data = {"challenge.$.score":int(score), "challenge.$.status":1}
        
        print searchCriteria
        print data
        
        #Update score and status for current user
        storageobj.updateArrayOneField('user', searchCriteria, data)
        
        #Update the stars for playing game
        storageobj.updateAndIncrement('user', 'username', username, {'StarsAchieved': 7})
        
        #Check if the opponent has played and if yes, check his score to decide who and won
        opponentRecord = storageobj.get('user', 'username', opponent)
        challengeArr = opponentRecord['challenge']
        
        for challengeRec in challengeArr:
            if ObjectId(pollId) == challengeRec['poll_id']:
                opponentStatus = challengeRec['status']
                opponentScore = int(challengeRec['score'])
                
        #----------Only if opponent has played ------
        if opponentStatus == 1:
            if opponentScore > score:
                winningUser = opponent
                losingUser = username
            else:
                winningUser = username
                losingUser = opponent
        
            #Update won field of both users
            storageobj.updateArrayOneField('user', {"username":losingUser, "challenge.poll_id":ObjectId(pollId)}
                                           , {"challenge.$.won":0}) 
            storageobj.updateArrayOneField('user', {"username":winningUser, "challenge.poll_id":ObjectId(pollId)}
                                           , {"challenge.$.won":1})
            
            #Update the stars for winning
            storageobj.updateAndIncrement('user', 'username', winningUser, {'StarsAchieved': 10})
            
            
        #---------------------------------------------
                
        return MongoEncoder().encode(status)

            
        
    except:
        traceback.print_exc()

#Ric End


#----------------------------------------------------------------------End --------------------------------------------------#

   
   




from django.contrib.auth import authenticate,login
from django.shortcuts import render_to_response
from django.template import RequestContext
import json, requests, base64
from django.http import *
import urllib2, urllib
from urllib2 import urlopen
from httplib import HTTP
from bson.objectid import ObjectId

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt


########## Clean code ####################################### 
#index page 
def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def nav(request):
    print 'Navigation bar loaded!'
    user = request.session['user']
    payload = {'username':user['username']}
    user = requests.put("http://127.0.0.1:8080/getProfile", data=json.dumps(payload))
    return render_to_response('nav.html', {'user':user.json()}, context_instance=RequestContext(request))

def progressbar(request):
    print 'progress bar loaded!'
    return render_to_response('test.html', context_instance=RequestContext(request))

def profnav(request):
    print 'Professor Navigation bar loaded!'
    return render_to_response('professorNav.html', context_instance=RequestContext(request))

#creating a user : register
def createUser(request):
   #print 'in create user'
   payload=''
   headers=''
   headers = {'content-type': 'application/json'}
   if request.method == 'POST':
      # save new post
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      fname = request.POST['firstname']
      lname = request.POST['lastname']
      education = request.POST['education']
      interests= []
      interests = request.POST.getlist('interest[]')
      #print interests
      organization = request.POST['organization']
      userType = request.POST['userType']
      #print 'USER TYPE -----> ' + userType
      encryptedpassword = base64.b64encode(password)
      if userType == 'Professor':
          payload = {"usertype": userType, "dbpayload": {"username":username, 'password':encryptedpassword, "email":email, "firstname":fname, "lastname":lname, "ContentId":[], "StarsAchieved":0, "currentContent":"", "organization":organization, "reco_attributes":{"highest_degree": education, "current_proficiency": request.POST['current_proficiency'], "current_status": request.POST['current_status'], "programming_languages": request.POST['programming_languages'], "interest_level": request.POST['interest_level'], "interests":interests}} }
      else:
          payload = {"usertype": userType, 
                     "dbpayload":
           {   
                "username":username, 
                'password':encryptedpassword, 
                "email":email, 
                "firstname":fname, 
                "lastname":lname,
                 "ContentId":[], 
                 "CourseCompletedPercentage":0, 
                 "currentContent":"", "StarsAchieved":0, 
                 "organization":organization,
                  "reco_attributes":{
                                     "highest_degree": education,
                                      "current_proficiency": request.POST['current_proficiency'],
                                       "current_status": request.POST['current_status'], 
                                       "programming_languages": request.POST['programming_languages'], 
                                       "interest_level": request.POST['interest_level'], 
                                       "interests":interests
                                       },
             "challenge": 
                        [
                                {"opponentUsername":"", "category":"category1","poll_id": "", "status":0, "score": 0, "won":-1},
                                {"opponentUsername":"", "category":"category2","poll_id": "", "status":0, "score": 0, "won":-1},
                                {"opponentUsername":"", "category":"category3","poll_id": "", "status":0, "score": 0, "won":-1},
                                {"opponentUsername":"", "category":"category4","poll_id": "", "status":0, "score": 0, "won":-1},
                                {"opponentUsername":"", "category":"category5","poll_id": "", "status":0, "score": 0, "won":-1},
                        ],
            }
        }
                 
      #print payload
      status=requests.post(url='http://127.0.0.1:8080/register',data=json.dumps(payload), headers=headers)
      #print status.status_code
      if(status.status_code==200):  
         #print status  
         return HttpResponseRedirect('http://127.0.0.1:8000/index')
      else:
          # TO DO: Change this to handle exceptions 
         return HttpResponseRedirect('http://google.com')
         #print status
   return render_to_response('Home.html', {'user': payload},context_instance=RequestContext(request))

# Render dashboard page
def dashboard(request):
    if request.session.get('isValid',True):
        print "In Dashboard"
        user = request.session['user']
        print "User"
        print request.session['user']
        payload = {"username":user['username']}
        content = requests.get("http://127.0.0.1:8080/getUserContent", data = json.dumps(payload))
        contents = content.json()
        print "Content"
        UserInfo = requests.put("http://127.0.0.1:8080/getProfile", data=json.dumps(payload))
        
        UserInfos = UserInfo.json()
        contentCount = requests.get("http://127.0.0.1:8080/getCount")
        contentCountJson = contentCount.json()
        print 'contentCount', contentCountJson
        UserInfos['TotalCount'] = contentCountJson
        print 'Total Count User', UserInfos['TotalCount']
        
        #print content.json()
#         for i in content:
#             print i
        NoOfContentsInCart= len(contents)
        user.update({'NoOfContentsInCart':NoOfContentsInCart})
        subCat = requests.put("http://127.0.0.1:8080/getCategoryCompletedPercentage", data=json.dumps(payload))
        print "Content--->",contents
        subCatPayload = subCat.json()
        subCatPayload['username'] = user['username']
        print 'updating all the category percentages'
        print 'subcategory payload -->', subCatPayload
        status = requests.put("http://127.0.0.1:8080/saveProfile", data=json.dumps(subCatPayload))
        print 'save profile ', status
        for content in contents:
            for content1 in UserInfos['contentCompleted']:
                if content['_id'] == content1['ContentId']:
                    #print content1['ContentId']
                    #print content1['ContentCompletedPercentage']
                    content['contentCompletedPercentage'] = content1['ContentCompletedPercentage']
        
        print contents
        
        rankedUsers = requests.get("http://127.0.0.1:8080/getRankedUsers")
        rankedUsersJson = rankedUsers.json()
        rank = 0
        for i in rankedUsersJson:
            rank = rank+1
            i['Rank'] = rank
            
        print "rankedUsers:", rankedUsersJson
       
        return render_to_response('dashboard.html', {'rankedUsers':rankedUsersJson,'user':UserInfos, 'content': contents, 'subCatPercentage':subCat.json()}, context_instance=RequestContext(request))
    else:
        print 'Session invalid'
        return HttpResponseRedirect("http://www.google.com")
    
# Render dashboard page
def professorDashboard(request):
    if request.session.get('isValid',True):
        user = request.session['user']
        print "User"
        print request.session['user']
        payload = {"username":user['username']}
        content = requests.get("http://127.0.0.1:8080/getProfessorContent", data = json.dumps(payload))
        print content
        return render_to_response('professorDashboard.html', {'user':request.session['user'], 'content': content.json()}, context_instance=RequestContext(request))
    else:
        print 'Session invalid'
        return HttpResponseRedirect("http://www.google.com")    

def signup(request):
    return render_to_response('signup.html', context_instance=RequestContext(request))
 

#For sign in 
def login_view(request):
    username = password = ''
    payload=''
    headers=''
    headers = {'content-type': 'application/json'}
    #print 'Views: In login'
    username = request.POST['username']
    password = request.POST['password']
    #print 'username', username
    #print 'password', password
    encryptedPassword = base64.b64encode(password)
    payload = {"username":username,"password":encryptedPassword}
    status=requests.put(url='http://127.0.0.1:8080/signIn', data=json.dumps(payload), headers=headers)
    #print status
    jsonData = status.json()
    #print jsonData
    if jsonData=={}:
        return render_to_response('loginfailed.html', context_instance=RequestContext(request))
    else:
        request.session['user'] = jsonData
        request.session['subcat'] = "1.1"
        request.session['isValid'] = True
        #print 'session --> ', request.session['user']
        return HttpResponseRedirect("/dashboard")

# For Professor Sign In    
def professor_login(request):
    
    state = "Please login below..."
    username = password = ''
    payload=''
    headers=''
    headers = {'content-type': 'application/json'}
    
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    encryptedPassword = base64.b64encode(password)
    payload = {"username":username,"password":encryptedPassword}
    
    status=requests.put(url='http://127.0.0.1:8080/professorSignIn', data=json.dumps(payload), headers=headers)
    jsonData = status.json()
    #print jsonData
    if jsonData==None:
        return render_to_response('loginfailed.html',{'username': username},context_instance=RequestContext(request))
    else:
        request.session['user'] = jsonData
        request.session['isValid'] = True
        #print 'session --> ', request.session['user']
        return HttpResponseRedirect("/professorDashboard")


    
def logout(request):
    try:
        #print 'Views: Logout'
        del request.session['user']
        del request.session['subcat']
        request.session['isValid']=False
    except KeyError:
        pass
    return HttpResponseRedirect("/index")

def courseContentSelection(request):
    print 'Django: In course content selection page'
#     status = requests.get(url='http://127.0.0.1:8080/courseContentSelection')
#     print status.json()
    print 'inside We Suggest'
    user = request.session['user']
    
    subcat = request.GET.get('subCat')
    request.session['subcategorySession'] = subcat
    
    print 'Session SubCategory', request.session['subcategorySession']
    if(subcat==None):
        subcat="1.1"
    subcatjson = {"subcat":subcat}
    print subcatjson
    print "Sub cat: " + subcat
    payload = {"username":user['username'], "sub_category":subcat}
    url = "http://127.0.0.1:8080/wesuggest/" #+ user['username']
    #data = urlopen(url).read()
    data=requests.get(url, data=json.dumps(payload))
    print "we suggest data"
    print data.json();
    payload = {"username":user['username']}
    content = requests.get("http://127.0.0.1:8080/getUserContent", data = json.dumps(payload))
    print "Content"
    print content.json()
    
    
    
   
    return render_to_response('courseContentSelection.html', {"data":data.json(), "content":content.json(), "subcat":subcatjson}, context_instance=RequestContext(request))


def edit_Profile(request):
    print 'Views: Edit profile'
    print request.session['user']
    user = request.session['user']
    payload = username = ''
    headers=''
    headers = {'content-type': 'application/json'}
    print 'username on wall' , user['firstname']
    username = user['username']
    payload = {'username':username}
    status=requests.put(url='http://127.0.0.1:8080/getProfile', data=json.dumps(payload), headers=headers)
    print 'STATUS_DATA ---> ', status.json()
    print status.status_code
    return render_to_response('editProfile.html',{ 'user':status.json()},context_instance=RequestContext(request))

def save_Profile(request):
    user = request.session['user']
    education = request.POST['education']
    interests= []
    interests = request.POST.getlist('interest[]')
    print interests
    country = request.POST['country']
    organization = request.POST['organization']
    
    payload = ''
    payload = {"username": user['username'], "education":education, "country":country, "interests":interests, "organization":organization }
    print "PAYLOAD ---> ", payload
    headers=''
    headers = {'content-type': 'application/json'}
    status=requests.post(url='http://127.0.0.1:8080/saveProfile', data=json.dumps(payload), headers=headers)
    print "result ---> ", status
    return HttpResponseRedirect("/dashboard")

########################################################################################

##############################Recommendation##################################
def subCatClicked(request):
    print 'inside sub cat clicked'
    subcat = request.GET.get('subcat');
   
    request.session['subcat'] = subcat;
    print request.session['subcat'];
    return HttpResponse()
    

def mostViewed(request):
    print 'inside most Viewed'
    url = "http://127.0.0.1:8080/mostviewedcontent"
    #data = urlopen(url).read()
    payload = {'sub_category':request.session['subcategorySession']}
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.put(url, data=json.dumps(payload), headers=headers)
    print data;
    # do whatever you want
    return HttpResponse(data, content_type="application/json")

def mostRated(request):
    print 'inside most Rated'
    url = "http://127.0.0.1:8080/mostratedcontent"
    #data = urlopen(url).read()
    payload = {'sub_category':request.session['subcategorySession']}
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.put(url, data=json.dumps(payload), headers=headers)
    print data;
    return HttpResponse(data, mimetype="application/json")

def viewAll(request):
    print 'inside view All'
    url = "http://127.0.0.1:8080/viewAll"
    payload = {'sub_category':request.session['subcategorySession']}
    print 'Session in View All: subcategory ', payload
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.put(url, data=json.dumps(payload), headers=headers)
    print data;
    return HttpResponse(data, mimetype="application/json")

def addToCart(request):
    print 'inside Add to cart'
    id = request.GET.get('courseId','')
    user = request.session['user']
    content = requests.put(url='http://127.0.0.1:8080/getContent', data=json.dumps({'id':id}))
    payload = {"username": user['username'], "contentId":id, 'sub_category':content.json()['sub_category']}
    print payload
    status=requests.post(url='http://127.0.0.1:8080/addToCart', data=json.dumps(payload))
    return HttpResponseRedirect("/courseContentSelection")
    
def removeContentFromCart(request):
	print 'inside remove content from cart'
	contentId = request.GET.get('contentId')
	if(contentId==None):
		contentId = request.GET.get('cartcontentId')
		user = request.session['user']
		payload = {"username":user['username'], "ContentId":contentId}
		print payload
		status = requests.post(url='http://127.0.0.1:8080/removeFromCart', data=json.dumps(payload))
		return HttpResponseRedirect("/courseContentSelection")
	else:
		user = request.session['user']
		payload = {"username":user['username'], "ContentId":contentId}
		print payload
		status = requests.post(url='http://127.0.0.1:8080/removeFromCart', data=json.dumps(payload))
		return HttpResponseRedirect("/dashboard")
	

def uploadQuestions(request):
    print 'request', request.POST
    headers=''
    headers = {'content-type': 'application/json'}
    totalQuestions = int(request.POST['numberOfQuestions'])
    print totalQuestions;
    finalPayload = []
    final = '';
    for eachQtn in range(0,totalQuestions):
        print 'inside for loop'
        question = request.POST['Question'+str(eachQtn+1)]
        optionA = request.POST['optionA'+str(eachQtn+1)]
        optionB = request.POST['optionB'+str(eachQtn+1)]
        optionC = request.POST['optionC'+str(eachQtn+1)]
        optionD = request.POST['optionD'+str(eachQtn+1)]
        answer = request.POST['answer'+str(eachQtn+1)]
        payload = {"Question":question, "Options":{"OptionA":optionA, "OptionB":optionB, "OptionC":optionC, "OptionD":optionD}, "Answer":answer}
        finalPayload.append(payload)
    
    contentName = request.POST['content_Name']
    final = {"Name":contentName, "payload":{"Questions": finalPayload}}
    
    status = requests.post(url='http://127.0.0.1:8080/uploadQuiz',data=json.dumps(final), headers=headers)    
    print status.status_code
    return HttpResponseRedirect("/professorDashboard")

def upload(request):
    print request.session['user']
    if request.POST:
            print 'VIEWS: In upload'
            payload=''
            headers=''
            headers = {'content-type': 'application/json'}
            contentName = request.POST['name']
            subCategory = request.POST['sub_category']
            description = request.POST['description']
            file = request.FILES['fileUpload']
            print 'file is posted from html'
            fileContent = file.read()
            print 'file read'
            path = default_storage.save(file.name, ContentFile(fileContent))
            print 'file is saved'
            print path 
            print default_storage.size(path)
            
            if path.find('pdf')>=0:
                print 'pdf uploaded'
                permalink = 'https://lh5.googleusercontent.com/-0ccxnhKgDkI/U0H2ASDlXyI/AAAAAAAABPw/f3TnC_FBgv0/s256-no/pdf-bbrfoundation.org_.png'
            elif path.find('mp4')>=0:
                print 'video uploaded'
                permalink = 'https://lh3.googleusercontent.com/-KRxBQzU8i2w/U0H19HjfN_I/AAAAAAAABPY/-wRt_DnBh0Q/s512-no/HiRes.jpg'
            else:
                print 'general file uploaded'
                permalink = 'http://www4.uwsp.edu/education/lwilson/newstuff/graphics/MCj03825740000[1].jpg'
            #print default_storage.open(path).read()
            

            user = request.session['user']
          
            username = user['username']
                        

            payload = {'Name':contentName, 'fileName':path, 'Description':description, 'sub_category':subCategory, "prof_username":username, "link":"", "Feedback":[], "RatingCount":0, "AverageRating": 0, "NoOfPeopleRated":0, "Type":"", "permalink": permalink, "count":0, "Questions":[]}

            print payload
            status=requests.post(url='http://127.0.0.1:8080/uploadContent',data=json.dumps(payload), headers=headers)
            print status.status_code
            return HttpResponseRedirect("/professorDashboard")
    return render_to_response('uploadContent.html', context_instance=RequestContext(request))

def courseDisplay(request):
    print 'in course'
    category = 0
    url = "http://127.0.0.1:8080/getCurrentContent"
    user = request.session['user'] #Getting user from session
    print user
    contentId = request.GET.get('contentId')  # getting content Id from Get URL from template
    
    username = user['username']
    print username
    print contentId
    user = requests.put("http://127.0.0.1:8080/getProfile", data=json.dumps({'username':username})) #Getting user 
    print user.json()
    user= user.json()
    # if content Id is not found 
    if contentId==None: 
        print 'No content id found'
       
        if user['currentContent']!="":
            contentId=user['currentContent']
        else: 
            print 'No current content too!'
            return HttpResponseRedirect('/courseContentSelection')
   
    request.session['currentContentId'] = contentId
    print contentId
    payload = {'contentId':contentId, 'username':user['username']}
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.put(url, data=json.dumps(payload), headers=headers)
    content = data.json()
    print content
    if content==None or content['sub_category']=="FirstTimeNoCurrentContent": 
        print content
        content={'NoContent': 'No Content Found. Please add a content'}
        print content
        return HttpResponseRedirect('/courseContentSelection')
    else:
        request.session['current_sub_category'] = content['sub_category']
        subCat = {'sub_category':content['sub_category']}
        print 'Poll: Sub Cat', subCat
        pollQuestions = requests.put("http://127.0.0.1:8080/getRandomPoll", data=json.dumps(subCat))
        for i in user['contentCompleted']: 
            if i['ContentId'] == content['_id']:
                content['percentage'] = i['ContentCompletedPercentage']
        print "New content with percentage", content;
        
        ##
        
        payload2 = {"username":user['username']}
        
        
        
        subCatPercentages = requests.put("http://127.0.0.1:8080/getCategoryCompletedPercentage", data=json.dumps(payload2))
        subCatPercentages1 = subCatPercentages.json()  
        print subCatPercentages1 
        if content['sub_category'] == "1.1" or content['sub_category'] == "1.2":
            print 'in category 1'
            category = 1
            request.session['current_category'] = 'category1'
            content['CategoryPercentage'] = subCatPercentages1['CategoryOnePercentage']
        if content['sub_category'] == "2.1" or content['sub_category'] == "2.2":
            print 'in category 2'
            category = 2
            request.session['current_category'] = 'category2'
            content['CategoryPercentage'] = subCatPercentages1['CategoryTwoPercentage']
        if content['sub_category'] == "3.1" or content['sub_category'] == "3.2":
            print 'in category 3'
            category = 3
            request.session['current_category'] = 'category3'
            content['CategoryPercentage'] = subCatPercentages1['CategoryThreePercentage']
        if content['sub_category'] == "4.1" or content['sub_category'] == "4.2":
            print 'in category 4'
            category = 4
            request.session['current_category'] = 'category4'
            content['CategoryPercentage'] = subCatPercentages1['CategoryFourPercentage']
        if content['sub_category'] == "5.1" or content['sub_category'] == "5.2":
            print 'in category 5'
            category = 5
            request.session['current_category'] = 'category5'
            content['CategoryPercentage'] = subCatPercentages1['CategoryFivePercentage']
        print 'CONTENT WITH ALL INFO:',content
        
        print 'category', category
        
        subCategory = {"sub_category":content['sub_category'], 'username':username}
        print 'sub Catgeory',subCategory 
        UsersOfCategory = requests.put("http://127.0.0.1:8080/getAllUsersOfCategory", data=json.dumps(subCategory))
        AllUsersJson = UsersOfCategory.json()
        print 'All Users-->', AllUsersJson
        
        
        #-----#
        for c in user['challenge']:
            if category==1 and c['category']=="category1":
                content['Category'] = category
                if c['poll_id']!="":
                    content['Challenge'] = 1 # 0 - will give and 1 - will take challenge
                else:
                    content['Challenge'] = 0
            if category==2 and c['category']=="category2":
                content['Category'] = category
                if c['poll_id']!="":
                    content['Challenge'] = 1
                else:
                    content['Challenge'] = 0
            if category==3 and c['category']=="category3":
                content['Category'] = category
                if c['poll_id']!="":
                    content['Challenge'] = 1
                else:
                    content['Challenge'] = 0
            if category==4 and c['category']=="category4":
                content['Category'] = category
                if c['poll_id']!="":
                    content['Challenge'] = 1
                else:
                    content['Challenge'] = 0
            if category==5 and c['category']=="category5":
                content['Category'] = category
                if c['poll_id']!="":
                    content['Challenge'] = 1
                else:
                    content['Challenge'] = 0
       
            
        print 'Challenge ', content['Challenge'] 
        return render_to_response('course.html', {'data':content, 'poll':pollQuestions.json(), 'user':user, 'subCatPercentages':subCatPercentages1, 'AllUsers':AllUsersJson}, context_instance=RequestContext(request))
       
    
    

def uploadQuiz(request):
     user = request.session['user']
     print "User"
     print request.session['user']
     payload = {"username":user['username']}
     content = requests.get("http://127.0.0.1:8080/getProfessorContent", data = json.dumps(payload))
     print content
     return render_to_response('uploadQuiz.html', {'content':content.json(), 'user':user}, context_instance=RequestContext(request))

def challengeCompleted(request):
    print 'in challenge Completed'
    headers=''
    headers = {'content-type': 'application/json'}
    user = request.session['user']
    username = user['username']
    sub_category = request.session['current_sub_category']
    contentId = request.session['currentContentId']
    payload = {'username':username, "sub_category":sub_category,"ChallengeQuestions":[], "contentId":contentId, "ChallengeTaken":1, "ContentCompletedPercentage":100, "QuizTaken":1}
    data = requests.put("http://127.0.0.1:8080/updateContentCompleted", data = json.dumps(payload),  headers=headers)
    print 'PAYLOAD -> ', payload
    print 'incrementing stars'
    payload1 = {"username":username, 'incValue':10}
    print 'payload stars', payload1
    status = requests.put("http://127.0.0.1:8080/incStars", data=json.dumps(payload1))
    print 'stars incremented', status
    return HttpResponseRedirect("/courseDisplay")

#------------------------------------------------Gamification --------------------------------------------------------------------------#
def afterQuiz(request):
     user = request.session['user']
     print "User"
     print request.session['user']
     payload = {"username":user['username']}
     content = requests.get("http://127.0.0.1:8080/getProfessorContent", data = json.dumps(payload))
     print content
     
     return render_to_response('uploadQuiz.html', {'content':content.json(), 'user':user}, context_instance=RequestContext(request))


def submitPoll(request):
    print 'in submit Poll'
    pollQuestionId= request.GET['pollQuestionId']
    print pollQuestionId
    answerSelected = request.POST['answer']
    print "Poll answer by user:"
   # qId = ObjectId(pollQuestionId)
    payload = {'pollQuestionId': pollQuestionId, 'optionId':answerSelected}
    gameQuestion = requests.put("http://127.0.0.1:8080/getSpecificPollQuestion", data=json.dumps(payload) )
    Question = gameQuestion.json()
    for i in Question['answers']:
        if answerSelected == i['optionId']:
            count = i['count']+1
    
    print count 
    payload1 = {'pollQuestionId': pollQuestionId, 'optionId':answerSelected, 'count':count}
    status = requests.put("http://127.0.0.1:8080/updatePolledQuestion", data=json.dumps(payload1))
    print answerSelected
    user = request.session['user']
    username = user['username']
    sub_category = request.session['current_sub_category']
    contentId = request.session['currentContentId']
    payload = {'username':username, "sub_category":sub_category,"ChallengeQuestions":[], "contentId":contentId, "ChallengeTaken":1, "ContentCompletedPercentage":100, "QuizTaken":1}
    data = requests.put("http://127.0.0.1:8080/updateContentCompleted", data = json.dumps(payload))
    print 'PAYLOAD -> ', payload
    print 'incrementing stars'
    payload1 = {"username":username, 'incValue':2}
    print 'payload stars', payload1
    status = requests.put("http://127.0.0.1:8080/incStars", data=json.dumps(payload1))
    print 'stars incremented', status
    return HttpResponseRedirect("/courseDisplay")

def playFeud(request):
    print 'inside play feud in views'
    opponentUsername = request.GET['opponentUsername']
    user = request.session['user']
    username = user['username']
    sub_category = request.session['current_sub_category'] 
    payload = {'username':username, 'sub_category':sub_category, "opponentUsername":opponentUsername}
    print 'PAYLOAD FOR FEUD --> ', payload
    status = requests.put("http://127.0.0.1:8080/playFeud", data = json.dumps(payload))
    #print 'FEUD QUESTION -> ', feudQuestion.json()
    return HttpResponseRedirect("/game")
    #return render_to_response('game.html', {'Polldata':feudQuestion.json()}, context_instance=RequestContext(request))

def game(request): 
    print 'inside game function'
    user = request.session['user']
    payload = {"username":user['username']}
    userProfile = requests.put("http://127.0.0.1:8080/getProfile", data = json.dumps(payload))
    player = userProfile.json()
    category = request.session['current_category'] 
    print 'Category in Game ', category
    challenge = player['challenge']
    for c in challenge:
        if c['category'] == 'category1':
            print "Category 1"
            print c['poll_id']
            questionId = c['poll_id']
            opponentUsername = c['opponentUsername']
            break;
        if c['category'] == 'category2':
            print "Category 1"
            print c['poll_id']
            questionId = c['poll_id']
            opponentUsername = c['opponentUsername']
            break;
        if c['category'] == 'category3':
            print "Category 1"
            print c['poll_id']
            questionId = c['poll_id']
            opponentUsername = c['opponentUsername']
            break;
        if c['category'] == 'category4':
            print "Category 1"
            print c['poll_id']
            questionId = c['poll_id']
            opponentUsername = c['opponentUsername']
            break;
        if c['category'] == 'category5':
            print "Category 1"
            print c['poll_id']
            questionId = c['poll_id']
            opponentUsername = c['opponentUsername']
            break;
    questionPayload = {"pollQuestionId":questionId}
    opponentPayload = {"username":opponentUsername}
    print 'opponent', opponentPayload
    opponent = requests.put("http://127.0.0.1:8080/getProfile", data=json.dumps(opponentPayload) )
    opponentJson = opponent.json()
    print 'Feud Question Id', questionPayload
    feudQuestion = requests.put("http://127.0.0.1:8080/getSpecificPollQuestion", data = json.dumps(questionPayload))
    feudQuestionJson = feudQuestion.json()
    print 'Feud Question', feudQuestionJson
    feudQuestionJson['category'] = category
    #userPayload = {"username":}
    #user = requests.put("http://127.0.0.1:8080/getProfile", data = json.dumps(Payload))
    return render_to_response('game.html', {'Polldata':feudQuestionJson, 'player':player, 'opponent':opponentJson}, context_instance=RequestContext(request))
    
def getQuiz(request, contentId):
    print 'inside getQuiz'
    url = "http://127.0.0.1:8080/getQuiz/" + contentId
    print 'url:', url
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.get(url, headers=headers)
    print 'Quiz data: ', data.json()
    return HttpResponse(data, mimetype="application/json")

@csrf_exempt
def submitQuizGrade(request):
    print 'you are in submit quiz grade view'
    data = request.POST
    username = request.session['user']['username']
    
    payload = {'username': username, 'data': {'contentId':data['contentId'], 'quiz_percentage':data['quiz_percentage']}}
    print payload
    status = requests.post("http://127.0.0.1:8080/submitQuizGrade", data = json.dumps(payload))

    print status
    
    #Rohit code to update content completed percentage value
    headers = {'content-type': 'application/json'}
    user = request.session['user']
    username = user['username']
    sub_category = request.session['current_sub_category']
    contentId = request.session['currentContentId']
    payload = {'username':username, "sub_category":sub_category,"ChallengeQuestions":[], "contentId":contentId, "ChallengeTaken":0, "ContentCompletedPercentage":60, "QuizTaken":1}
    print 'PAYLOAD -> ', payload
    data = requests.put("http://127.0.0.1:8080/updateContentCompleted", data = json.dumps(payload),  headers=headers)
    print 'incrementing stars'
    payload1 = {"username":username, 'incValue':3}
    print 'payload stars', payload1
    status = requests.put("http://127.0.0.1:8080/incStars", data=json.dumps(payload1))
    print 'stars incremented', status
    
    print 'incrementing content count'
    payload2 = {"contentId": contentId}
    print 'payload content count', payload2
    status1 = requests.put("http://127.0.0.1:8080/incContentCount", data=json.dumps(payload2))
    print 'content count', status1
    #------------------------End of Rohit code ------------------------------#
    
    return HttpResponse(status, mimetype="application/json")

@csrf_exempt
def updateContentRating(request):
    print 'in update content rating'
    
    # increment NoOfPeopleRated by 1 
    
    contentId = request.POST['contentId']
    rating = request.POST['Rating']
    payload = {"id":contentId}
    status1 = requests.put("http://127.0.0.1:8080/updateAndIncNoOfPeopleRated", data=json.dumps(payload))
    print status1
    print 'Incremented NoOfPeopleRated by 1'
    
    # Add RatingCount by the present rating given 
    
    payload10 = {'id':contentId, 'RatingCount':rating}
    status10 = requests.put("http://127.0.0.1:8080/updateAndAddRatingCount", data=json.dumps(payload10))
    print status10
    print 'updated and added Rating count'
    
    #get content - NoOfPeopleRated and Rating count and compute average rating
    
    content = requests.put("http://127.0.0.1:8080/getContent", data=json.dumps(payload))
    contentJson = content.json()
    AverageRating=0
    RatingCount = contentJson['RatingCount']
    NoOfPeopleRated = contentJson['NoOfPeopleRated']
    AverageRating = RatingCount/NoOfPeopleRated
    print 'Average Rating : ', AverageRating
    
    #Update averageRating
    payload2 = {'id':contentId, 'AverageRating':AverageRating}
    status2 = requests.put("http://127.0.0.1:8080/updateAverageRating", data=json.dumps(payload2))
    print status2
    print 'Average Rating updated'
    
    return HttpResponse(status2, mimetype="application/json")

@csrf_exempt
def endGame(request):
    data = {}
    data['category'] = request.session['current_category']
    data['pollId'] = request.POST['pollId']
    data['opponent'] = request.POST['opponent']
    data['username'] = request.session['user']['username']
    data['score'] = request.POST['score']
    
    requests.post("http://127.0.0.1:8080/endGame", data = json.dumps(data))
    
    return HttpResponse({"sample":"sample"}, mimetype="application/json")

#Ric End

#------------------------------------------------Gamification --------------------------------------------------------------------------#










   

        

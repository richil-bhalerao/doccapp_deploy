from django.contrib.auth import authenticate,login
from django.shortcuts import render_to_response
from django.template import RequestContext
import json, requests, base64
from django.http import *
import urllib2, urllib
from urllib2 import urlopen
from httplib import HTTP
from .forms import UploadFileForm


########## Clean code ####################################### 
#index page 
def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))


#creating a user : register
def createUser(request):
   print 'in create user'
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
      print interests
      organization = request.POST['organization']
      userType = request.POST['userType']
      print 'USER TYPE -----> ' + userType
      
      encryptedpassword = base64.b64encode(password)
      if userType == 'Professor':
          payload = {"usertype": userType, "dbpayload": {"username":username, 'password':encryptedpassword, "email":email, "firstname":fname, "lastname":lname, "ContentId":[], "ContentCompleted":[], "organization":organization, "reco_attributes":{"highest_degree": education, "current_proficiency": request.POST['current_proficiency'], "current_status": request.POST['current_status'], "programming_languages": request.POST['programming_languages'], "interest_level": request.POST['interest_level'], "interests":interests}} }
      else:
          payload = {"usertype": userType, "dbpayload": {"username":username, 'password':encryptedpassword, "email":email, "firstname":fname, "lastname":lname, "ContentId":[], "ContentCompleted":[], "organization":organization, "reco_attributes":{"highest_degree": education, "current_proficiency": request.POST['current_proficiency'], "current_status": request.POST['current_status'], "programming_languages": request.POST['programming_languages'], "interest_level": request.POST['interest_level'], "interests":interests}} }
     
      print payload
      status=requests.post(url='http://127.0.0.1:8080/register',data=json.dumps(payload), headers=headers)
      print status.status_code
      if(status.status_code==200):  
         print status  
         return HttpResponseRedirect('http://127.0.0.1:8000/index')
      else:
          # TO DO: Change this to handle exceptions 
         return HttpResponseRedirect('http://google.com')
         print status
   return render_to_response('Home.html', {'user': payload},
                             context_instance=RequestContext(request))

# Render dashboard page
def dashboard(request):
    if request.session.get('isValid',True):
        print "In Dashboard"
        user = request.session['user']
        print "User"
        print request.session['user']
        payload = {"username":user['username']}
        content = requests.get("http://127.0.0.1:8080/getUserContent", data = json.dumps(payload))
        print "Content"
        print content.json()
#         for i in content:
#             print i
        return render_to_response('dashboard.html', {'user':request.session['user'], 'content': content.json()}, context_instance=RequestContext(request))
    else:
        print 'Session invalid'
        return HttpResponseRedirect("http://www.google.com")
    
# Render dashboard page
def professorDashboard(request):
    if request.session.get('isValid',True):
        print request.session['user']
        return render_to_response('professorDashboard.html', {'user':request.session['user']}, context_instance=RequestContext(request))
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
    print 'Views: In login'
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    encryptedPassword = base64.b64encode(password)
    payload = {"username":username,"password":encryptedPassword}
    status=requests.put(url='http://127.0.0.1:8080/signIn', data=json.dumps(payload), headers=headers)
    print status
    jsonData = status.json()
    print jsonData
    if jsonData=={}:
        return render_to_response('loginfailed.html', context_instance=RequestContext(request))
    else:
        request.session['user'] = jsonData
        request.session['isValid'] = True
        print 'session --> ', request.session['user']
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
    print jsonData
    if jsonData==None:
        return render_to_response('loginfailed.html',{'username': username},context_instance=RequestContext(request))
    else:
        request.session['user'] = jsonData
        request.session['isValid'] = True
        print 'session --> ', request.session['user']
        return HttpResponseRedirect("/professorDashboard")

    
def logout(request):
    try:
        print 'Views: Logout'
        del request.session['user']
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
    payload = {"username":user['username']}
    url = "http://127.0.0.1:8080/wesuggest/" #+ user['username']
    #data = urlopen(url).read()
    data=requests.get(url, data=json.dumps(payload))
    print data.json();
    # do whatever you want
    return render_to_response('courseContentSelection.html', {"data":data.json()}, context_instance=RequestContext(request))


def edit_Profile(request):
    print 'Views: Edit profile'
    print request.session['user']
    user = request.session['user']
    payload = username = ''
    headers=''
    headers = {'content-type': 'application/json'}
    print 'username on wall' , user['fname']
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

def mostViewed(request):
    print 'inside most Viewed'
    url = "http://127.0.0.1:8080/mostviewedcontent"
    #data = urlopen(url).read()
    payload = {'sub_category':"sub1"}
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.put(url, data=json.dumps(payload), headers=headers)
    print data;
    # do whatever you want
    return HttpResponse(data, mimetype="application/json")

def mostRated(request):
    print 'inside most Rated'
    url = "http://127.0.0.1:8080/mostratedcontent"
    #data = urlopen(url).read()
    payload = {'sub_category':"sub1"}
    headers=''
    headers = {'content-type': 'application/json'}
    data=requests.put(url, data=json.dumps(payload), headers=headers)
    print data;
    return HttpResponse(data, mimetype="application/json")

def viewAll(request):
    print 'inside view All'
    url = "http://127.0.0.1:8080/viewAll"
    data = urlopen(url).read()
    print data
    # do whatever you want
    return HttpResponse(data, mimetype="application/json")

def addToCart(request):
    print 'inside Add to cart'
    id = request.GET.get('courseId','')
    user = request.session['user']
    payload = {"username": user['username'], "contentId":id}
    print payload
    status=requests.post(url='http://127.0.0.1:8080/addToCart', data=json.dumps(payload))
    return HttpResponseRedirect("/courseContentSelection")




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
            file = request.POST['fileUpload']
            user = request.session['user']
            username = user['username']
            print file
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                print 'in form valid'
                handle_uploaded_file(request.FILES['file'])
            
            payload = {'Name':contentName, 'Description':description, 'sub_category':subCategory, "prof_username":username, "link":"", "Feedback":[], "Rating": 0, "Type":""}
            print payload
            status=requests.post(url='http://127.0.0.1:8080/uploadContent',data=json.dumps(payload), headers=headers)
            print status.status_code
            return HttpResponseRedirect("/professorDashboard")
    return render_to_response('uploadContent.html', context_instance=RequestContext(request))


def handle_uploaded_file(f):
    with open('/home/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            print chunk
            destination.write(chunk)

















   

        

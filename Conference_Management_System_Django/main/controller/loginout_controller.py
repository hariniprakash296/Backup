from django.shortcuts import render
from django.http import HttpResponse,Http404
from main.controller import controller_util
from main import models
import hashlib
from main import Utils
from threading import Lock
from threading import Thread
from conferencesystem import settings
import datetime
from django.core.files.storage import FileSystemStorage
import os
from main import constants
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import smart_str
from django.shortcuts import redirect
from main.controller import controller_util
import random

email_lock = Lock()

def create_login_cookies(response,email,hashed_password,non_hashed_user_type):
    max_age = 60 * 30
    hashed_user_type = controller_util.hash_string(non_hashed_user_type)
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key="email", value=email, max_age=max_age, expires=expires)
    response.set_cookie(key="password", value=hashed_password, max_age=max_age, expires=expires)
    response.set_cookie(key="user_type", value=hashed_user_type, max_age=max_age, expires=expires)
	
#view funcs	
def index(request, message=None):
    islogged_in = controller_util.check_login(request)
    is_admin_logged_in = controller_util.check_type_login(request, models.User.UserType.USERTYPE_SYSTEMADMIN)

    user_type = request.COOKIES.get('user_type')
    if user_type:
        if user_type == controller_util.hash_string(str(models.User.UserType.USERTYPE_SYSTEMADMIN)):
            #0 = system admin
            template_name = "admin_homepage.html"
            
        elif user_type == controller_util.hash_string(str(models.User.UserType.USERTYPE_CONFERENCECHAIR)):
            #1 = conference chair
            template_name = "conferencechair_homepage.html"
            
        elif user_type == controller_util.hash_string(str(models.User.UserType.USERTYPE_REVIEWER)):
            #2 = reviewer
            template_name = "reviewer_homepage.html"
            
        elif user_type == controller_util.hash_string(str(models.User.UserType.USERTYPE_AUTHOR)):
            #3 = author
            template_name = "author_homepage.html"
    else:
        template_name = "index.html"

    context = {"islogged_in":islogged_in,"is_admin_logged_in":is_admin_logged_in,"user_type":request.COOKIES.get('user_type')}

    if message != None and not "message" in context:
        context["message"] = message

    #print("Using template: "+template_name)
    return render(request,template_name,context)
	
def login(request):
    islogged_in = False
    is_admin_logged_in = False
    return render(request,"login.html",{"islogged_in":islogged_in,'message':"","is_admin_logged_in":is_admin_logged_in,"user_type":request.COOKIES.get('user_type')})

def login_ValidateInfo(request):
    if request.method == "POST":
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password').strip()
        
        password = password.encode('utf-8')
        hashed_password = hashlib.sha224(password).hexdigest()
        user_type = None
        max_age = 60 * 30
        try:
            user = models.User.objects.get(login_email=email,login_pw=hashed_password)
            try:
                user_type = user.user_type

                if user_type == models.User.UserType.USERTYPE_SYSTEMADMIN:
                    #0 = system admin
                    template_name = "admin_homepage.html"
                    
                elif user_type == models.User.UserType.USERTYPE_CONFERENCECHAIR:
                    #1 = conference chair
                    template_name = "conferencechair_homepage.html"
                    
                elif user_type == models.User.UserType.USERTYPE_REVIEWER:
                    #2 = reviewer
                    template_name = "reviewer_homepage.html"
                    
                elif user_type == models.User.UserType.USERTYPE_AUTHOR:
                    #3 = author
                    template_name = "author_homepage.html"
                    
                hashed_user_type = controller_util.hash_string(str(user_type))
                context = {"islogged_in":True, "is_admin_logged_in":user_type == models.User.UserType.USERTYPE_SYSTEMADMIN, "user_type":controller_util.hash_string(str(user_type)), 'message':"Logged in as "+user.name}
                response = render(request, template_name, context)
                #response = render(request, "index.html", context)

                expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                                        "%a, %d-%b-%Y %H:%M:%S GMT")
                                                        
                response.set_cookie(key="email", value=email, max_age=max_age, expires=expires)
                response.set_cookie(key="password", value=hashed_password, max_age=max_age, expires=expires) 
                response.set_cookie(key="user_type", value=hashed_user_type, max_age=max_age, expires=expires)
                
                return response
            except Exception as e:
                print(e)
                return HttpResponse("Unexpected error. Exception : ",e)
        except Exception as e:
            # Non existing user
            print(e)
            return render(request,"login.html",{"islogged_in":False, 'message':'Bad Authentication.', "is_admin_logged_in":False
                                                , "user_type":request.COOKIES.get('user_type')})
													
def logout_handle(request):
    response = render(request, "login.html", {"islogged_in": False,"is_admin_logged_in":False, 'message':'Logged out successfully.'})
    response.delete_cookie('user_type')
    response.delete_cookie('email')
    response.delete_cookie('password')
    return response

def emergency_manual_method(request):
    # call via "http://127.0.0.1:8000/emergency_manual_method?user_id="
    # if request.method == "GET":
    #     try:
    #         user_id = request.GET.get('user_id')
    #         user = models.User.objects.get(user_id=user_id)
    #         user.delete()
    #     except Exception as e:
    #         print(e)

    for paper in models.Paper.objects.all():
        if paper.paper_name == "":
            paper.paper_name = "Temp Title"
            paper.save()

    return index(request)

def test_template(request):
    # call via "http://127.0.0.1:8000/test_template"

    # template_name = "conferencechair_listsubmittedpapers.html"
    template_name = "conferencechair_listreviewers.html"

    return render(request,template_name,{"islogged_in":False, 'message':'Bad Authentication.', "is_admin_logged_in":False
                                                , "user_type":request.COOKIES.get('user_type')})

def create_users(request):
    print(os.getcwd())
    password_file_name = "../namelist.txt"
    if not os.path.exists(password_file_name):
        raise Exception("Password file does not exist.")
    fr = open(password_file_name, "r")
    string_names = fr.read().splitlines()
    fr.close()
    #return index(request)

    string_names = list(set(string_names))

    user_type_choices = range(models.User.UserType.USERTYPE_SYSTEMADMIN, models.User.UserType.USERTYPE_AUTHOR+1)
        
    for i in range(120):
        string_name = string_names[i]
    
        name = string_name.split(",")[0]

        user_type = random.choice(user_type_choices)
        email = name.lower()+"@gmail.com"
        password = "password".encode('utf-8')
        max_papers = random.randint(5,10)

        hashed_password = hashlib.sha224(password).hexdigest()
        try:
            user = models.User.objects.get(login_email=email)
            continue

        except models.User.DoesNotExist as e:
            print("creating "+str(user_type))
            if user_type == models.User.UserType.USERTYPE_SYSTEMADMIN:
                #0 = system admin
                models.SystemAdmin.objects.create(login_email=email, login_pw=hashed_password, name=name, user_type=models.User.UserType.USERTYPE_SYSTEMADMIN)
                
            elif user_type == models.User.UserType.USERTYPE_CONFERENCECHAIR:
                #1 = conference chair
                models.ConferenceChair.objects.create(login_email=email, login_pw=hashed_password, name=name, user_type=models.User.UserType.USERTYPE_CONFERENCECHAIR)
                
            elif user_type == models.User.UserType.USERTYPE_REVIEWER:
                #2 = reviewer
                models.Reviewer.objects.create(login_email=email, login_pw=hashed_password, name=name, max_papers=max_papers, user_type=models.User.UserType.USERTYPE_REVIEWER)
                
            elif user_type == models.User.UserType.USERTYPE_AUTHOR:
                #3 = author
                models.Author.objects.create(login_email=email, login_pw=hashed_password, name=name, user_type=models.User.UserType.USERTYPE_AUTHOR)

    return index(request, "")


from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
     # Uncomment the admin/doc line below to e(r'^register/$','mysite.users.views.createUser'),nable admin documentation:
    url(r'^admin/', include(admin.site.urls)),
    
    (r'^signIn/$','mysite.users.views.login_view'),
    (r'^welcome/$','mysite.users.views.save_Profile'),
    (r'^professorSignIn/$','mysite.users.views.professor_login'),
    (r'^editProfile/$','mysite.users.views.edit_Profile'),
    (r'^index/$','mysite.users.views.index'),
    (r'^logout/$','mysite.users.views.logout'),
    (r'^course/$','mysite.users.views.addcourse'),
     (r'^register/$','mysite.users.views.createUser'),
     (r'^courseContentSelection/$','mysite.users.views.courseContentSelection'),
     (r'^addToCart/$','mysite.users.views.addToCart'),
    (r'^dashboard/$','mysite.users.views.dashboard'), 
    (r'^professorDashboard/$','mysite.users.views.professorDashboard'), 
    (r'^mostViewed/$','mysite.users.views.mostViewed'),
    (r'^mostRated/$','mysite.users.views.mostRated'),
     (r'^viewAll/$','mysite.users.views.viewAll')  
)

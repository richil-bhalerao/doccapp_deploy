from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

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
      (r'^signup/$','mysite.users.views.signup'),
     (r'^register/$','mysite.users.views.createUser'),
     (r'^courseContentSelection/$','mysite.users.views.courseContentSelection'),
     (r'^courseContentSelection/subCatClicked$','mysite.users.views.subCatClicked'),
     (r'^addToCart/$','mysite.users.views.addToCart'),
    (r'^removeContentFromCart/$','mysite.users.views.removeContentFromCart'),
      (r'^playFeud/$','mysite.users.views.playFeud'),
                      
    (r'^dashboard/$','mysite.users.views.dashboard'), 
    (r'^professorDashboard/$','mysite.users.views.professorDashboard'), 
    (r'^mostViewed/$','mysite.users.views.mostViewed'),
    (r'^mostRated/$','mysite.users.views.mostRated'),
     (r'^viewAll/$','mysite.users.views.viewAll'),  
     (r'^upload/$','mysite.users.views.upload'),
     (r'^uploadQuiz/$','mysite.users.views.uploadQuiz'),
     (r'^challengeCompleted/$','mysite.users.views.challengeCompleted'),
     (r'^uploadQuestions/$','mysite.users.views.uploadQuestions'),
     (r'^nav/$','mysite.users.views.nav'), 
     (r'^game/$','mysite.users.views.game'), 
     (r'^profnav/$','mysite.users.views.profnav'), 
      (r'^courseDisplay/$','mysite.users.views.courseDisplay'), 
      (r'^submitPoll/$','mysite.users.views.submitPoll'),
      (r'^updateRating/$','mysite.users.views.updateContentRating'),
    (r'^getQuiz/([a-zA-Z0-9_]*)$','mysite.users.views.getQuiz'),
    (r'^submitQuizGrade/$','mysite.users.views.submitQuizGrade'),
    (r'^endGame/$','mysite.users.views.endGame'),
       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}),
)

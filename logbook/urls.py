from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.indexView, name = 'index'),
    url(r'^books/$', views.booksView, name = 'books'),
    url(r'^faq/$', views.faqView, name = 'faq'),
    url(r'^add/$', views.addLogbookView, name='addLogbook'),
    url(r'^signup/$', views.signupView, name = 'signup'),
    url(r'^superSignup/$', views.supervisorSignupView, name = 'superSignup'),
    url(r'^login/$', views.loginView, name = 'login'),
    url(r'^logout/$', views.logoutView, name = 'logout'),
    url(r'^profile/$', views.profileView, name = 'profile'),
    url(r'^(?P<username>[0-9]{8})/(?P<logbook_name_slug>[\w\-]+)/$',
        views.logentryView, name = 'logentry'),
    url(r'^(?P<username>[0-9]{8})/(?P<logbook_name_slug>[\w\-]+)/add/$',
        views.addLogEntryView, name='addLogEntry'),
    ]

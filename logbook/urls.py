from django.conf.urls import url
from . import views

app_name = 'logbook'
urlpatterns = [
    url(r'^$', views.indexView, name='index'),
    url(r'^faq/$', views.faqView, name='faq'),
    url(r'^create/$', views.addLogbookView, name='create'),
    url(r'^signup/$', views.signupView, name='signup'),
    url(r'^signup/supervisor/$', views.supervisorSignupView, name='super_signup'),
    url(r'^login/$', views.loginView, name='login'),
    url(r'^logout/$', views.logoutView, name='logout'),
    url(r'^profile/$', views.profileView, name='profile'),
    url(r'^b/$', views.booksView, name='list'),
    url(r'^b/(?P<pk>[0-9]+)/$',
        views.logentryView, name='view'),
    url(r'^b/(?P<pk>[0-9]+)/add/$',
        views.addLogEntryView, name='add_entry'),
    ]

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.indexView, name = 'index'),
    url(r'^signup/$', views.signupView, name = 'signup'),
    url(r'^login/$', views.loginView, name = 'login'),
    url(r'^logout/$', views.logoutView, name = 'logout'),
    url(r'^profile/$', views.profileView, name = 'profile'),
    ]

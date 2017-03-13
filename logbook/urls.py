from django.conf.urls import url
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete 
from . import views

app_name = 'logbook'
urlpatterns = [
    url(r'^$', views.indexView, name='index'),
    url(r'^faq/$', views.faqView, name='faq'),
    url(r'^create/$', views.addLogbookView, name='create'),
    url(r'^accounts/signup/$', views.signupView, name='signup'),
    url(r'^activate/(?P<key>.+)$', views.activation, name = 'activate'),
    url(r'^new-activation-link/(?P<user_id>[0-9]+)/$', views.new_activation_link, name = 'new_activation_link'),
    url(r'^accounts/signup/supervisor/$', views.supervisorSignupView, name='super_signup'),
    url(r'^accounts/login/$', views.loginView, name='login'),
    url(r'^accounts/logout/$', views.logoutView, name='logout'),
    url(r'^accounts/password_reset/$', password_reset, {'post_reset_redirect':'/logbook/accounts/password_reset/done'}, name='password_reset'),
    url(r'^accounts/password_reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, {'post_reset_redirect':'/logbook/accounts/reset/done/'},
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$', password_reset_complete, name='password_reset_complete'),
    url(r'^profile/$', views.profileView, name='profile'),
    url(r'^delete_user/$', views.deleteUserView, name='delete_user'),
    url(r'^edit_names/$', views.editNamesView, name='edit_names'),
    url(r'^b/$', views.booksView, name='list'),
    url(r'^b/(?P<pk>[0-9]+)/$',views.logentryView, name='view'),
    url(r'^b/(?P<pk>[0-9]+)/add/$',views.addLogEntryView, name='add_entry'),
    url(r'^b/(?P<pk>[0-9]+)/create_supervisor/$',views.createSupervisorView, name='create_super'),
    url(r'^b/(?P<pk>[0-9]+)/(?P<log_id>[0-9]+)/edit/$',views.editLogEntryView, name='edit_entry'),
    ]

from django.conf.urls import url
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete 
from . import views

app_name = 'logbook'
urlpatterns = [
    url(r'^$', views.indexView, name='index'),
    url(r'^faq/$', views.faqView, name='faq'),
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
    url(r'^b/load_book/$', views.loadBookView, name='load_book'),
    url(r'^b/edit_book/$', views.editLogBookView, name='edit_book'),
    url(r'b/update_approvals/$', views.updateHoursList, name='update_hours'),
    url(r'^b/(?P<pk>[0-9]+)/$',views.logEntryView, name='view'),
    url(r'^b/(?P<pk>[0-9]+)/create_supervisor/$',views.createTempSupervisorView, name='create_super'),
    url(r'b/(?P<pk>[0-9]+)/add_entry', views.addLogEntryView, name='add_entry'),
    url(r'b/load_entry/$', views.loadEntryView, name='load_entry'),
    url(r'b/(?P<pk>[0-9]+)/edit_entry/$', views.editLogEntryView, name='edit_entry'),
    url(r'^search/$', views.searchBarView, name='search_bar'),
    ]

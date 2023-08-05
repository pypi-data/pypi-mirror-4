from django.conf.urls import patterns, include, url

urlpatterns = patterns('django_proxy_users.views',

    url(r'^$', 'home', name='home'),
    url(r'^login/$', 'login', name='login'),
    url(r'^login/as/$', 'login_as', name='login_as'),
    url(r'^log/back/in/as/$', 'log_back_in_as', name='log_back_in_as'),
    url(r'^logout/$', 'logout', name='logout'),

)

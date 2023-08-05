from django.conf.urls.defaults import *
#from openid_consumer.views import complete, signout
from django.views.generic.simple import direct_to_template

#Login Views
urlpatterns = patterns('socialauth.views',
    url(r'^inicio$', 'facebook_login', name='socialauth_login'),
    url(r'^procesar$', 'facebook_login_done', name='socialauth_done'),
)

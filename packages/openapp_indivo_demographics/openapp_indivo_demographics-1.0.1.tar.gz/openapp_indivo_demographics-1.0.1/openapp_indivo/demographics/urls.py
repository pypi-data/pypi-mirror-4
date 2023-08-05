
# URLs for a simple Django Application

from django.conf.urls.defaults import patterns
from views import start_auth, after_auth, demographics, edit

urlpatterns = patterns('',
    (r'^start_auth', start_auth),
    (r'^after_auth', after_auth),
    (r'^(?P<sessionkey>.+)/demographics$', demographics), 
    (r'^(?P<sessionkey>.+)/edit$', edit), 
)


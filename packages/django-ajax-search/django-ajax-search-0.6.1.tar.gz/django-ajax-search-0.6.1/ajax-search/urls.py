from django.conf.urls.defaults import *

from ajax-search import views

urlpatterns = patterns('',
	url(r'^xhr_search$','views.xhr_search'),
)

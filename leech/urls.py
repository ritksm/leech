from django.conf.urls import patterns, include, url
from leech.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'leech_devel.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^generate/$', GenerateView.as_view(), name='generate'),
    url(r'^go/(?P<slug>\w+)', SlugRedirectView.as_view(), name='redirect'),
)
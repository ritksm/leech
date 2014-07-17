from django.conf.urls import patterns, include, url
from leech.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'leech_devel.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^generate/$', GenerateView.as_view(), name='generate'),
    url(r'^go/(?P<slug>\w+)/$', SlugRedirectView.as_view(), name='redirect'),
    url(r'^api/generate/$', APIGenerateView.as_view(), name='api-generate'),
    url(r'^api/click_count/(?P<slug>\w+)/$', APIClickCountView.as_view(), name='api-click-count'),
    url(r'^stat/(?P<slug>\w+)/$', StatisticView.as_view(), name='statistic'),
    url(r'^remarks/$', RemarksEditView.as_view(), name='remarks'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^slug/source/edit/', ChangeSourceUrlView.as_view(), name='change-source-url'),
    url(r'^stat/total_click_count/reset/(?P<slug>\w+)/', ResetSlugTotalClickCountView.as_view(),
        name='reset-total-click-count'),
    url(r'^slug/hide/(?P<slug_id>\d+)/', HideSlugView.as_view(), name='hide-slug'),
)
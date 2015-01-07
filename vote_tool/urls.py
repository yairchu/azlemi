from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'vote.views.home'),
    url(r'^get_question/$', 'vote.views.get_question'),
    url(r'^get_question/(?P<question_id>[0-9]+)/$', 'vote.views.get_specific_question'),
    url(r'^admin/', include('smuggler.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'vote.views.home'),
    url(r'^get_question/$', 'vote.views.get_question'),
    url(r'^admin/', include(admin.site.urls)),
)

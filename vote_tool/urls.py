from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'vote.views.home'),
    url(r'^publish/(?P<votes_str>[^/]+)/$', 'vote.views.publish'),
    url(r'^publish/(?P<votes_str>[^/]+)/image.(?P<extension>[a-z]+)$', 'vote.views.publish_image'),
    url(r'^get_question/$', 'vote.views.get_question'),
    url(r'^save_vote/$', 'vote.views.save_vote'),
    url(r'^restart/$', 'vote.views.restart'),
    url(r'^get_question/(?P<question_id>[0-9]+)/$', 'vote.views.get_specific_question'),
    url(r'^admin/', include('smuggler.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'', include('feincms.urls'))
)

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from solid_i18n.urls import solid_i18n_patterns

urlpatterns = patterns('',
    url(r'^save_vote/$', 'vote.views.save_vote'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
) + solid_i18n_patterns('',
    url(r'^$', 'vote.views.home'),
    url(r'^publish/(?P<votes_str>[^/]+)/$', 'vote.views.publish'),
    url(r'^publish/(?P<votes_str>[^/]+)/image.(?P<extension>[a-z]+)$', 'vote.views.publish_image'),
    url(r'^get_question/$', 'vote.views.get_question'),
    url(r'^get_question/(?P<question_ids>[0-9,\,]+)/$', 'vote.views.get_specific_question'),
    url(r'^restart/$', 'vote.views.restart'),
    url(r'^admin/recent_actions/$',
        login_required(login_url='/admin/login/')(
            TemplateView.as_view(template_name='admin/recent_actions.html'))),
    url(r'^admin/', include('smuggler.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

urlpatterns += patterns('',
    url(r'', include('feincms.urls'))
)

### MONKEY PATCHES FOR DJANGO BUGS:

# https://github.com/django/django/pull/4060
import django.contrib.admin.templatetags.log
class AdminLogNode(django.contrib.admin.templatetags.log.AdminLogNode):
    def render(self, context):
        from django import template
        from django.contrib.admin.models import LogEntry
        if self.user is None:
            entries = LogEntry.objects.all()
        else:
            user_id = self.user
            if not user_id.isdigit():
                user_id = context[self.user].pk
            entries = LogEntry.objects.filter(user__pk=user_id)
        context[self.varname] = entries.select_related(
            'content_type', 'user',
            )[:int(self.limit)]
        return ''
django.contrib.admin.templatetags.log.AdminLogNode = AdminLogNode

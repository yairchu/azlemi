from django import forms
from django.conf import settings
from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from vote import models

def vote_form_widgets():
    result = {}
    for field in ['title', 'vt_title', 'vt_description']:
        suffixes = ['']
        if field.startswith('vt_'):
            suffixes = ['_he', '_en']
        for suffix in suffixes:
            attrs = {'cols': 100, 'rows': 1}
            if 'description' in field:
                attrs['rows'] = 20
            if suffix in ['', '_he']:
                attrs['dir'] = 'rtl'
            result[field+suffix] = forms.Textarea(attrs=attrs)
    return result

class VoteForm(forms.ModelForm):
    class Meta:
        model = models.Vote
        exclude = []
        widgets = vote_form_widgets()

class HasTranslationFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.request = request
        super(HasTranslationFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.title = '%s Translations' % (field.verbose_name)

    def expected_parameters(self):
        for lang_key, lang_name in settings.LANGUAGES[1:]:
            yield '%s_%s__exact' % (self.field_path, lang_key)
            yield '%s_%s__gt' % (self.field_path, lang_key)

    def choices(self, cl):
        params = set()
        any_chosen = False
        for param in self.expected_parameters():
            params.add(param)
            is_chosen = self.request.GET.get(param) == ''
            any_chosen = any_chosen or is_chosen
        yield {
            'selected': not any_chosen,
            'display': 'Any',
            'query_string': cl.get_query_string({}, params),
            }
        for lang_key, lang_name in settings.LANGUAGES[1:]:
            for op, desc in [('exact', 'Lacks'), ('gt', 'Has')]:
                param = '%s_%s__%s' % (self.field_path, lang_key, op)
                is_chosen = self.request.GET.get(param) == ''
                yield {
                    'selected': is_chosen,
                    'display': '%s %s' % (desc, lang_name),
                    'query_string': cl.get_query_string({param: ''}, params),
                    }

class VoteAdmin(TabbedTranslationAdmin):
    form = VoteForm
    list_filter = ['is_interesting', ('vt_title', HasTranslationFilter)]

admin.site.register(models.UserAnswer)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.Publish)

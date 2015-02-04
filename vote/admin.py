from django import forms
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

class VoteAdmin(TabbedTranslationAdmin):
    form = VoteForm
    list_filter = ['is_interesting']

admin.site.register(models.UserAnswer)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.Publish)

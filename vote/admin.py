from django import forms
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from vote import models

class VoteForm(forms.ModelForm):
    class Meta:
        model = models.Vote
        exclude = []
        widgets = {
            'vt_description_he':
                forms.Textarea(attrs={'cols': 80, 'rows': 20, 'dir': 'rtl'}),
            'vt_description_en':
                forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class VoteAdmin(TranslationAdmin):
    form = VoteForm
    list_filter = ['is_interesting']

admin.site.register(models.UserAnswer)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.Publish)

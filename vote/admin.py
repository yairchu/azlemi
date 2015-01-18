from django import forms
from django.contrib import admin

from vote import models

class VoteForm(forms.ModelForm):
    class Meta:
        model = models.Vote
        exclude = []
        widgets = {
            'vt_description':
                forms.Textarea(attrs={'cols': 80, 'rows': 20, 'dir': 'rtl'}),
        }

class VoteAdmin(admin.ModelAdmin):
    form = VoteForm
    list_filter = ['is_interesting']

admin.site.register(models.UserAnswer)
admin.site.register(models.Vote, VoteAdmin)

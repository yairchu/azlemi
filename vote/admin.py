from django.contrib import admin

from vote import models

class VoteAdmin(admin.ModelAdmin):
    list_filter = ['is_interesting']

admin.site.register(models.UserAnswer)
admin.site.register(models.Vote, VoteAdmin)

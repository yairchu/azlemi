from django.contrib import admin

from vote import models

admin.site.register(models.UserAnswer)
admin.site.register(models.Vote)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0009_publish'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='vt_description_en',
            field=models.CharField(default='', null=True, max_length=2000, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vote',
            name='vt_description_he',
            field=models.CharField(default='', null=True, max_length=2000, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vote',
            name='vt_title_en',
            field=models.CharField(default='', null=True, max_length=120, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vote',
            name='vt_title_he',
            field=models.CharField(default='', null=True, max_length=120, blank=True),
            preserve_default=True,
        ),
    ]

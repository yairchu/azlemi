# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0011_auto_20150204_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='vt_description_ru',
            field=models.CharField(null=True, blank=True, default='', max_length=2000),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='vote',
            name='vt_title_ru',
            field=models.CharField(null=True, blank=True, default='', max_length=140),
            preserve_default=True,
        ),
    ]

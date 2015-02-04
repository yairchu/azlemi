# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0010_auto_20150203_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='vt_title',
            field=models.CharField(max_length=140, blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='vt_title_en',
            field=models.CharField(null=True, max_length=140, blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vote',
            name='vt_title_he',
            field=models.CharField(null=True, max_length=140, blank=True, default=''),
            preserve_default=True,
        ),
    ]

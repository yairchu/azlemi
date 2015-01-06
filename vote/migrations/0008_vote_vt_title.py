# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0007_vote_vt_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='vt_title',
            field=models.CharField(max_length=120, default='', blank=True),
            preserve_default=True,
        ),
    ]

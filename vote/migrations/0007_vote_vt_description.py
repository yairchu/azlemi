# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0006_vote_is_interesting'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='vt_description',
            field=models.CharField(blank=True, max_length=2000, default=''),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0005_auto_20141231_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='is_interesting',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

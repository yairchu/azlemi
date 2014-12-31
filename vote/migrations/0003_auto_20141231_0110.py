# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0002_useranswer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useranswer',
            name='session',
        ),
        migrations.AddField(
            model_name='useranswer',
            name='session_key',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]

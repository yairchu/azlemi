# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0004_manual_20141231_1636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='session_key',
            field=models.CharField(null=True, max_length=100),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0002_auto_20150203_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='language',
            field=models.CharField(choices=[('he', 'Hebrew'), ('en', 'English'), ('ru', 'Russian')], max_length=10, default='he', verbose_name='language'),
            preserve_default=True,
        ),
    ]

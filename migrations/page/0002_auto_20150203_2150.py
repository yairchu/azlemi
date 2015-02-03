# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='language',
            field=models.CharField(verbose_name='language', max_length=10, default='he', choices=[('he', 'Hebrew'), ('en', 'English')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='translation_of',
            field=models.ForeignKey(to='page.Page', help_text='Leave this empty for entries in the primary language.', blank=True, verbose_name='translation of', null=True, related_name='translations'),
            preserve_default=True,
        ),
    ]

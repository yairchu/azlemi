# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('session_key', models.CharField(max_length=40, verbose_name='session key', primary_key=True, serialize=False)),
                ('session_data', models.TextField(verbose_name='session data')),
                ('expire_date', models.DateTimeField(verbose_name='expire date', db_index=True)),
            ],
            options={
                'verbose_name_plural': 'sessions',
                'verbose_name': 'session',
                'db_table': 'django_session',
            },
            bases=(models.Model,),
        ),
    ]

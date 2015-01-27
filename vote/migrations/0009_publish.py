# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0008_vote_vt_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publish',
            fields=[
                ('key', models.CharField(serialize=False, max_length=50, primary_key=True)),
                ('votes', models.CharField(max_length=2000)),
                ('when', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('vote', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('answer', models.IntegerField()),
                ('when', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(to='sessions.Session')),
                ('vote', models.ForeignKey(to='vote.Vote', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

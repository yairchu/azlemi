# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0012_auto_20150205_1905'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoteToDistinguishParties',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('party_a', models.CharField(max_length=100)),
                ('party_b', models.CharField(max_length=100)),
                ('vote', models.ForeignKey(to='vote.Vote')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

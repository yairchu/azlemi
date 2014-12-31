# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('oknesset_data', models.BinaryField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
import json

from django.db import models, migrations

def extract_fields(apps, schema_editor):
    Vote = apps.get_model('vote', 'Vote')
    for vote in Vote.objects.all():
        data = json.loads(bytes(vote.oknesset_data).decode('utf8'))
        vote.against_votes_count = data['against_votes_count']
        vote.for_votes_count = data['for_votes_count']
        vote.title = data['title']
        vote.save()

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('vote', '0003_auto_20141231_0110'),
    ]
    operations = [
        migrations.AddField(
            model_name='vote',
            name='against_votes_count',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vote',
            name='for_votes_count',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vote',
            name='title',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.RunPython(extract_fields, noop),
    ]

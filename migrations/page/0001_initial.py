# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import feincms.contrib.richtext
import feincms.extensions
import feincms.module.mixins


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('title', models.CharField(help_text='This title is also used for navigation menu items.', max_length=200, verbose_name='title')),
                ('slug', models.SlugField(help_text='This is used to build the URL for this page', max_length=150, verbose_name='slug')),
                ('in_navigation', models.BooleanField(default=False, verbose_name='in navigation')),
                ('override_url', models.CharField(help_text="Override the target URL. Be sure to include slashes at the beginning and at the end if it is a local URL. This affects both the navigation and subpages' URLs.", max_length=255, blank=True, verbose_name='override URL')),
                ('redirect_to', models.CharField(help_text='Target URL for automatic redirects or the primary key of a page.', max_length=255, blank=True, verbose_name='redirect to')),
                ('_cached_url', models.CharField(max_length=255, default='', blank=True, verbose_name='Cached URL', db_index=True, editable=False)),
                ('template_key', models.CharField(max_length=255, default='page.html', verbose_name='template', choices=[('page.html', 'Standard template')])),
                ('parent', models.ForeignKey(verbose_name='Parent', null=True, blank=True, related_name='children', to='page.Page')),
            ],
            options={
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
                'ordering': ['tree_id', 'lft'],
            },
            bases=(models.Model, feincms.extensions.ExtensionsMixin, feincms.module.mixins.ContentModelMixin),
        ),
        migrations.CreateModel(
            name='RichTextContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('text', feincms.contrib.richtext.RichTextField(blank=True, verbose_name='text')),
                ('region', models.CharField(max_length=255)),
                ('ordering', models.IntegerField(default=0, verbose_name='ordering')),
                ('parent', models.ForeignKey(related_name='richtextcontent_set', to='page.Page')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'rich text',
                'ordering': ['ordering'],
                'verbose_name_plural': 'rich texts',
                'db_table': 'page_page_richtextcontent',
                'permissions': [],
            },
            bases=(models.Model,),
        ),
    ]

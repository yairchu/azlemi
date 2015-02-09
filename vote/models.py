import json

from django.contrib.sessions.models import Session
from django.db import models

from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent

Page.register_templates({
    'title': 'Standard template',
    'path': 'page.html',
    'regions': (
        ('main', 'Main content area'),
    ),
})
Page.create_content_type(RichTextContent)
Page.register_extensions('feincms.module.extensions.translations')

class Vote(models.Model):
    id = models.IntegerField(primary_key=True) # consistent with oknesset's ids
    title = models.CharField(max_length=1000)
    for_votes_count = models.IntegerField()
    against_votes_count = models.IntegerField()

    oknesset_data = models.BinaryField()
    is_interesting = models.BooleanField(default = False)
    vt_title = models.CharField(max_length=140, blank=True, default='')
    vt_description = models.CharField(max_length=2000, blank=True, default='')
    def __str__(self):
        return '%s %d: %s' % (
            'INTERESTING VOTE' if self.is_interesting else 'vote',
            self.id, self.vt_title or self.title
            )

class UserAnswer(models.Model):
    session_key = models.CharField(max_length=100, null=True)
    # No vote means which party user votes for
    vote = models.ForeignKey(Vote, null=True)
    answer = models.IntegerField()
    when = models.DateTimeField(auto_now=True)
    def __str__(self):
        if self.vote is None:
            t = 'pp=%d' % self.answer
        else:
            t = 'q%d=%d' % (self.vote.id, self.answer)
        return 'UserAnswer %s session=%s when=%s' % (t, self.session_key, self.when)

class Publish(models.Model):
    key = models.CharField(primary_key=True, max_length=50)
    votes = models.CharField(max_length=2000)
    when = models.DateTimeField(auto_now=True)
    def __str__(self):
        return 'Publish %s when=%s' % (self.key, self.when)

class VoteToDistinguishParties(models.Model):
    vote = models.ForeignKey(Vote)
    # The party coming alphabetically first should be first
    party_a = models.CharField(max_length=100)
    party_b = models.CharField(max_length=100)

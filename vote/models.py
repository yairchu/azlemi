import json

from django.contrib.sessions.models import Session
from django.db import models

class Vote(models.Model):
    id = models.IntegerField(primary_key=True) # consistent with oknesset's ids
    title = models.CharField(max_length=1000)
    for_votes_count = models.IntegerField()
    against_votes_count = models.IntegerField()

    oknesset_data = models.BinaryField()
    is_interesting = models.BooleanField(default = False)
    vt_title = models.CharField(max_length=120, blank=True, default='')
    vt_description = models.CharField(max_length=2000, blank=True, default='')
    def __str__(self):
        return '%s %d: %s' % (
            'INTERESTING VOTE' if self.is_interesting else 'vote',
            self.id, self.title
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

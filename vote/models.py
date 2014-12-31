import json

from django.contrib.sessions.models import Session
from django.db import models

class Vote(models.Model):
    id = models.IntegerField(primary_key=True) # consistent with oknesset's ids
    oknesset_data = models.BinaryField()
    def __str__(self):
        desc = json.loads(bytes(self.oknesset_data).decode('utf8'))['title']
        return 'Vote %d: %s' % (self.id, desc)

class UserAnswer(models.Model):
    session = models.ForeignKey(Session)
    # No vote means which party user votes for
    vote = models.ForeignKey(Vote, null=True)
    answer = models.IntegerField()
    when = models.DateTimeField(auto_now=True)
    def __str__(self):
        if self.vote is None:
            t = 'pp=%d' % self.answer
        else:
            t = 'q%d=%d' % (self.vote.id, self.answer)
        return 'UserAnswer %s session=%s when=%s' % (t, self.session.session_key, self.when)

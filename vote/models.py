import json

from django.db import models

class Vote(models.Model):
    id = models.IntegerField(primary_key=True) # consistent with oknesset's ids
    oknesset_data = models.BinaryField()
    def __str__(self):
        desc = json.loads(bytes(self.oknesset_data).decode('utf8'))['title']
        return 'Vote %d: %s' % (self.id, desc)

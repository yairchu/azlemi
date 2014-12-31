import json
import os
import random
import urllib.request

from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.shortcuts import render

from vote import models

oknesset_path = os.path.dirname(__file__)+'/../vote_tool/static/oknesset'
votes_meta = json.load(open(oknesset_path+'/api/v2/vote/_limit=1'))['meta']
num_votes = votes_meta['total_count']

def track_changes(request):
    prev_state = request.session.get('state', {})
    request.session['state'] = request.GET
    for k, v in request.GET.items():
        if v == prev_state.get(k):
            continue
        if k.startswith('q'):
            vote = models.Vote.objects.get(id=int(k[1:]))
        else:
            vote = None
        models.UserAnswer(
            session_key=request.session.session_key,
            vote=vote, answer=int(v)).save()

def fetch_vote(vote_id):
    try:
        vote = models.Vote.objects.get(id=vote_id)
    except models.Vote.DoesNotExist:
        # import vote from oknesset
        raw_json = urllib.request.urlopen(
            'https://oknesset.org/api/v2/vote/%d/' % vote_id).read()
        vote = models.Vote(id=vote_id, oknesset_data=raw_json)
        vote.save()
    return bytes(vote.oknesset_data).decode('utf8')

def get_question(request):
    track_changes(request)
    already_asked = set(
        int(x[1:]) for x in request.GET.keys() if x.startswith('q'))
    did_not_ask = set(range(1, num_votes+1)) - already_asked
    vote_raw_json = fetch_vote(random.choice(list(did_not_ask)))
    return HttpResponse(vote_raw_json)

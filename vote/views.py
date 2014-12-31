import json
import os
import random
import urllib.request

from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.shortcuts import render

from vote import models

dirname = os.path.dirname(__file__)
oknesset_path = dirname+'/../vote_tool/static/oknesset'
votes_meta = json.load(open(oknesset_path+'/api/v2/vote/_limit=1'))['meta']
num_votes = votes_meta['total_count']

def home(request):
    context = {
        'parties':
            str(dict(
            (int(x['id']), x) for x in
            json.loads(open(oknesset_path+'/api/v2/party').read())['objects']
            )),
        'members':
            str(json.loads(open(dirname+'/data/member_info.json').read())),
        }
    return render(request, 'vote/home.html', context)

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
        data = json.loads(raw_json.decode('utf8'))
        vote = models.Vote(
            id=vote_id, oknesset_data=raw_json,
            against_votes_count = data['against_votes_count'],
            for_votes_count = data['for_votes_count'],
            title = data['title'],
            )
        vote.save()
    return vote

def get_question(request):
    track_changes(request)

    already_asked = set(
        int(x[1:]) for x in request.GET.keys() if x.startswith('q'))

    vote = None
    if random.random() < 0.8:
        # 80% of the time ask existing interesting questions from db
        # 20% of the time will ask totally random question
        interesting_votes_in_db = models.Vote.objects.filter(
            for_votes_count__gte = 10, against_votes_count__gte = 10)
        interesting_votes_in_db = [
            x for x in interesting_votes_in_db
            if x.id not in already_asked]
        if interesting_votes_in_db:
            vote = random.choice(interesting_votes_in_db)
    if vote is None:
        did_not_ask = set(range(1, num_votes+1)) - already_asked
        vote = fetch_vote(random.choice(list(did_not_ask)))
    vote_raw_json = bytes(vote.oknesset_data).decode('utf8')
    return HttpResponse(vote_raw_json)

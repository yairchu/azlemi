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
    parties = json.loads(open(oknesset_path+'/api/v2/party').read())['objects']
    short_names = {
      'חזית דמוקרטית לשלום ושוויון': 'חד״ש',
      'ברית לאומית דמוקרטית': 'בל״ד',
      }
    for p in parties:
        name = short_names.get(p['name'])
        if name:
            p['short_name'] = name

    start_votes = list(models.Vote.objects.filter(is_interesting = True))
    random.shuffle(start_votes)
    start_votes = [export_vote(x) for x in start_votes[:2]]

    context = {
        'parties': parties,
        'members': json.loads(open(dirname+'/data/member_info.json').read()),
        'questions': start_votes,
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

def choose_question_set(already_asked):
    result = set()
    r = random.random()
    if r < 0.6:
        result = set(
            x.id for x in
            models.Vote.objects.filter(is_interesting = True)
            ) - already_asked
    if not result and r < 0.8:
        result = set(
            x.id for x in
            models.Vote.objects.filter(
                for_votes_count__gte = 10, against_votes_count__gte = 10)
            ) - already_asked
    if not result:
        result = set(range(1, num_votes+1)) - already_asked
    return result

def export_vote(vote):
    vote_raw_json = bytes(vote.oknesset_data).decode('utf8')
    vote_json = json.loads(vote_raw_json)
    for key in ['vt_title', 'vt_description']:
        val = getattr(vote, key, None)
        if val:
            vote_json[key] = val
    return vote_json

def get_specific_question(request, question_id = None):
    return HttpResponse(json.dumps(export_vote(fetch_vote(int(question_id)))))

def get_question(request):
    track_changes(request)
    already_asked = set(
        int(x[1:]) for x in request.GET.keys() if x.startswith('q'))
    question_set = choose_question_set(already_asked)
    question_id = random.choice(list(question_set))
    return HttpResponse(json.dumps(export_vote(fetch_vote(question_id))))

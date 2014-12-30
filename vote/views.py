import json
import os
import random
import urllib.request

from django.http import HttpResponse
from django.shortcuts import render

oknesset_path = os.path.dirname(__file__)+'/../vote_tool/static/oknesset'
votes_meta = json.load(open(oknesset_path+'/api/v2/vote/_limit=1'))['meta']
num_votes = votes_meta['total_count']

def get_question(request):
    already_asked = set(
        int(x[1:]) for x in request.GET.keys() if x.startswith('q'))
    did_not_ask = set(range(1, num_votes+1)) - already_asked
    vote_id = random.choice(list(did_not_ask))

    vote_raw_json = urllib.request.urlopen(
        'https://oknesset.org/api/v2/vote/%d/' % vote_id
        ).read().decode('utf8')
    return HttpResponse(vote_raw_json)

import json
import os
import random
import urllib.request

from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from browser import html

from vote import models
from vote import render_content

dirname = os.path.dirname(__file__)

class CommonData:
    oknesset_path = dirname+'/data/oknesset/api/v2'
    def __init__(self):
        self.data = {}
    def __getitem__(self, key):
        if key not in self.data:
            self.data['key'] = getattr(self, 'load_'+key)()
        return self.data['key']
    def load_num_votes(self):
        return json.load(open(self.oknesset_path+'/vote/_limit=1')
            )['meta']['total_count']
    def load_members(self):
        return json.loads(open(dirname+'/data/member_info.json').read())
    def load_party_of_member(self):
        return dict((x['id'], x['party_id']) for x in self['members'])
    def load_parties(self):
        parties = json.loads(open(
            self.oknesset_path+'/party/_knesset=all').read())['objects']
        short_names = {
          'חזית דמוקרטית לשלום ושוויון': 'חד״ש',
          'ברית לאומית דמוקרטית': 'בל״ד',
          }
        for p in parties:
            name = short_names.get(p['name'])
            if name:
                p['short_name'] = name
        return dict((x['id'], x) for x in parties if x['knesset_id'] == 19)
common_data = CommonData()

def home(request):
    state = request.session.get('state', {})
    prev_question_ids = [
        int(x[1:])
        for x in request.session.get('questions_order', [])
        if x.startswith('q')]
    print(prev_question_ids)
    prev_questions = [
        export_vote(v) for v in
        models.Vote.objects.filter(id__in=tuple(prev_question_ids))]
    # sort prev_questions by order
    prev_questions = dict((q['id'], q) for q in prev_questions)
    prev_questions = [prev_questions[qid] for qid in prev_question_ids]

    rendered_prevs_questions = []
    user_answers = {}
    for question in prev_questions:
        panel, party_votes_doc, radios = render_content.question_panel(question)
        answer = int(state['q%d'%question['id']])
        user_answers[question['id']] = answer
        for radio in radios:
            if int(radio.attrs['value']) == answer:
                radio.attrs['checked'] = 'true'
        render_content.question_party_votes(
            party_votes_doc, question, answer, common_data['parties'])
        rendered_prevs_questions.append(str(panel))
    results = render_content.calc_results(
        dict((q['id'], q) for q in prev_questions),
        user_answers,
        common_data['parties']
        )
    results_html = html.TBODY(id='results')
    small_results_html = html.DIV(id="results-small", style={'color': 'gray'})
    render_content.render_results(
        results_html, small_results_html, results, common_data['parties'])

    start_votes = [
        x for x in
        models.Vote.objects.filter(is_interesting = True)
        if x.id not in prev_question_ids
        ]
    random.shuffle(start_votes)
    start_votes = [export_vote(x) for x in start_votes[:3]]

    if start_votes:
        question = start_votes.pop()
        prev_questions.append(question)
        panel, _, _ = render_content.question_panel(question)
        rendered_prevs_questions.append(str(panel))

    context = {
        'parties_dict': common_data['parties'],
        'members': common_data['members'],
        'prev_questions': prev_questions,
        'prev_questions_html': '\n'.join(rendered_prevs_questions),
        'questions': start_votes,
        'results_html': results_html,
        'small_results_html': small_results_html,
        }
    return render(request, 'vote/home.html', context)

def track_changes(request):
    prev_state = request.session.get('state', {})
    if 's' in request.GET:
        t = [x.split(':') for x in request.GET['s'].split(',')]
        request.session['state'] = dict(t)
        request.session['questions_order'] = [x[0] for x in t]
    else:
        request.session['state'] = {}
        request.session['questions_order'] = []
    for k, v in request.session['state'].items():
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
    if random.random() < 0.9:
        result = set(
            x.id for x in
            models.Vote.objects.filter(is_interesting = True)
            ) - already_asked
    if not result and random.random() < 0.6:
        result = set(
            x.id for x in
            models.Vote.objects.filter(
                for_votes_count__gte = 10, against_votes_count__gte = 10)
            ) - already_asked
    if not result:
        result = set(range(1, common_data['num_votes']+1)) - already_asked
    return result

def export_vote(vote):
    vote_raw_json = bytes(vote.oknesset_data).decode('utf8')
    vote_json = json.loads(vote_raw_json)
    for key in ['vt_title', 'vt_description']:
        val = getattr(vote, key, None)
        if val:
            vote_json[key] = val
    party_votes = {}
    for vote in vote_json['votes']:
        def id_from_uri(uri):
            return int(uri.rstrip('/').rsplit('/', 1)[1])
        party_id = common_data['party_of_member'][id_from_uri(vote['member'])]
        party_res = party_votes.setdefault(party_id, {})
        vote_type = vote['vote_type']
        party_res[vote_type] = 1 + party_res.get(vote_type, 0)
    vote_json['party_votes'] = party_votes
    return vote_json

def get_specific_question(request, question_id = None):
    return HttpResponse(json.dumps(export_vote(fetch_vote(int(question_id)))))

def get_question(request):
    track_changes(request)

    already_asked = list(request.session['state'].keys())
    queue = request.GET.get('queue', '')
    if queue:
        already_asked += queue.split(',')
    already_asked = set( int(x[1:]) for x in already_asked if x.startswith('q'))

    question_set = choose_question_set(already_asked)
    question_id = random.choice(list(question_set))
    return HttpResponse(json.dumps(export_vote(fetch_vote(question_id))))

def save_vote(request):
    track_changes(request)
    return HttpResponse('ok')

def restart(request):
    request.session['state'] = {}
    request.session['questions_order'] = []
    return HttpResponseRedirect('/')

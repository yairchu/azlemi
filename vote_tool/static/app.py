#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import ajax, document, html, timer

class Question:
    vals = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

    def __init__(self, data):
        self.data = data
        self.answer = None

        document['questions'] <= html.H4(self.data['title'])
        summary = html.P()
        if self.data['summary']:
            for block in self.data['summary'].split('<br>'):
                if not block.strip():
                    continue
                summary <= block
                summary <= html.BR()
        summary <= html.A('מידע נוסף',
            href='https://oknesset.org/vote/%d/' % self.data['id'])
        document['questions'] <= summary
        uservote = html.P()
        uservote <= 'הצבעתך:'
        self.radios = []
        for val, name in self.vals:
            radio = html.INPUT(type='radio', name=str(self.data['id']), value=str(val))
            radio.bind('change', self.set_answer)
            self.radios.append(radio)
            uservote <= radio
            uservote <= name
        document['questions'] <= uservote
        self.party_votes_doc = html.P()
        document['questions'] <= self.party_votes_doc

    def set_answer(self, event):
        first_answer = self.answer is None
        self.answer = int(radio_val(self.radios))

        if first_answer:
            self.calc_party_votes()
            self.show_party_votes()

        game.update_results()
        if first_answer:
            timer.request_animation_frame(self.add_question)

    def calc_party_votes(self):
        self.party_votes = {}
        for vote in self.data['votes']:
            if 'for' == vote['vote_type']:
                val = 1
            elif 'against' == vote['vote_type']:
                val = -1
            else:
                continue
            party_id = party_of_member[id_from_uri(vote['member'])]
            if not party_id in parties:
                continue
            party_results = self.party_votes.setdefault(party_id, {-1: 0, 1: 0})
            party_results[val] += 1

    def show_party_votes(self):
        def key(x):
            results = x[1]
            return -sum(results.values())
        for party_id, results in sorted(self.party_votes.items(), key=key):
            party = parties[party_id]
            txt = party['name']+':'
            if results[1]:
                txt += ' %d בעד' % results[1]
            if results[-1]:
                txt += ' %d נגד' % results[-1]
            txt += ' (מתוך %d), ' % party['number_of_seats']
            self.party_votes_doc <= txt

    def add_question(self, *args):
        game.add_question()

class Game:
    def __init__(self):
        self.questions = {}
    def set_party(self, event):
        prev_party = radio_val(party_radios)
        self.prev_party = int(prev_party) if prev_party else 0
        if self.questions:
            self.update_results()
        else:
            self.add_question()
    def add_question(self):
        req = ajax.ajax()
        req.bind('complete', self.got_question)
        params = ['pp=%d' % self.prev_party]
        for question_id, question in self.questions.items():
            params.append('q%d=%d' % (question_id, question.answer))
        req.open('GET', '/get_question/?'+'&'.join(params))
        req.send()
    def got_question(self, req):
        assert req.status in [0, 200]
        question_data = json.loads(req.text)
        question_id = question_data['id']
        assert question_id not in self.questions
        question = Question(question_data)
        self.questions[question_id] = question
    def update_results(self):
        results = {}
        num_questions = 0
        for question in self.questions.values():
            if not question.answer:
                continue
            num_questions += 1
            for party_id, votes in question.party_votes.items():
                party_results = results.setdefault(party_id, {-1: 0, 1: 0})
                for k, v in votes.items():
                    party_results[k * question.answer] += v
        document['results'].clear()
        if not num_questions:
            return
        for party_id, s in results.items():
            s['overall'] = s[1] - s[-1]
            max_count = parties[party_id]['number_of_seats'] * num_questions
            for k in s.keys():
                s[k] /= max_count

        table = html.TABLE()
        row = html.TR()
        row <= html.TH('מפלגה')
        row <= html.TH('איתך')
        row <= html.TH('נגדך')
        row <= html.TH('סה״כ')
        table <= row
        def key(x):
            return -x[1]['overall']
        for party_id, score in sorted(list(results.items()), key=key):
            if party_id not in parties:
                # party_id is per knesset session at the moment
                # and the oknesset api doesn't give data for old sessions
                # see https://oknesset.org/party/5/ ("ישראל ביתנו בכנסת ה-18")
                continue
            row = html.TR()
            party_name = parties[party_id]['name']
            if party_id == self.prev_party:
                party_name = html.B(party_name)
            row <= html.TD(party_name)
            for k in [1, -1, 'overall']:
                row <= html.TD('%.0f%%'%(100*score[k]), dir='ltr')
            table <= row
        document['results'] <= html.H3('תוצאות:')
        document['results'] <= table

def id_from_uri(uri):
    return int(uri.rstrip('/').rsplit('/', 1)[1])

def radio_val(radios):
    for radio in radios:
        if radio.checked:
            return radio.value

game = Game()

parties = json.loads(open('oknesset/api/v2/party').read())['objects']
parties = dict((x['id'], x) for x in parties)

members = json.loads(open('data/member_info.json').read())
party_of_member = dict((x['id'], x['party_id']) for x in members)

party_radios = []

def party_entry(val, name):
    radio = html.INPUT(type='radio', name='previous_vote', value=val)
    radio.bind('change', game.set_party)
    party_radios.append(radio)
    document['previous_vote'] <= radio
    document['previous_vote'] <= name

parties_list = html.UL()
party_entry('', 'לא הצבעתי')
for party in parties.values():
    party_entry(party['id'], party['name'])

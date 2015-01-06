#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import ajax, document, html, timer

class Question:
    vals = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

    def __init__(self, data):
        self.data = data
        self.answer = None

        document['questions'] <= html.H3(
            self.data.get('vt_title') or self.data['title'])
        summary = html.P()
        description = self.data.get('vt_description') or self.data['summary']
        if description:
            for block in description.split('<br>'):
                if not block.strip():
                    continue
                summary <= block
                summary <= html.BR()
        summary <= html.A('מידע נוסף',
            href='https://oknesset.org/vote/%d/' % self.data['id'])
        document['questions'] <= summary
        uservote = html.P()
        self.radios = []
        for val, name in self.vals:
            label = html.LABEL()
            btn_div = html.DIV(**{'class': 'btn btn-lg btn-default'})
            label <= btn_div
            radio = html.INPUT(type='radio', name=str(self.data['id']), value=str(val))
            radio.bind('change', self.set_answer)
            self.radios.append(radio)
            btn_div <= radio
            btn_div <= ' '+name+' '
            uservote <= label
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
        self.party_votes_doc.clear()
        if self.answer is None:
            return
        def key(x):
            results = x[1]
            return (x[0] != game.prev_party, -sum(results.values()))
        if game.prev_party != 0 and game.prev_party not in self.party_votes:
            self.party_votes_doc <= html.B(
                '%s לא הצביעה. ' % parties[game.prev_party]['name'])
        for party_id, results in sorted(self.party_votes.items(), key=key):
            party = parties[party_id]
            txt = party['name']+':'
            if results[1]:
                txt += ' %d בעד' % results[1]
            if results[-1]:
                txt += ' %d נגד' % results[-1]
            txt += ' (מתוך %d), ' % party['number_of_seats']
            if party_id == game.prev_party:
                txt = html.B(txt)
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
            for question in self.questions.values():
                question.show_party_votes()
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
        if req.status not in [0, 200]:
            document['debug'].html = req.text
            return
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

        table = document['results']
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
                cell = '%.0f%%'%(100*score[k])
                if party_id == self.prev_party:
                    cell = html.B(cell)
                row <= html.TD(cell, dir='ltr')
            table <= row

def id_from_uri(uri):
    return int(uri.rstrip('/').rsplit('/', 1)[1])

def radio_val(radios):
    for radio in radios:
        if radio.checked:
            return radio.value

game = Game()

party_of_member = dict((x['id'], x['party_id']) for x in members)

party_radios = document['previous_vote'].get(selector='INPUT')
for radio in party_radios:
    radio.bind('change', game.set_party)

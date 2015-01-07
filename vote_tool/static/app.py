#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import ajax, document, html, timer
from browser.local_storage import storage

for q in questions:
    q['raw_json'] = json.dumps(q)
party_of_member = dict((x['id'], x['party_id']) for x in members)

class Question:
    vals = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

    def __init__(self, data, loaded=False):
        self.data = data
        self.id = data['id']
        self.answer = None

        question = html.DIV(**{'class': 'panel panel-primary'})
        document['questions'] <= question
        title = self.data.get('vt_title')
        if not title:
            title = self.data['title']
            for prefix in [
                'להעביר את הצעת החוק לוועדה - ',
                'להעביר את הצעת החוק לוועדה שתקבע ועדת הכנסת - ',
                ]:
                if title.startswith(prefix):
                    title = title[len(prefix):]
                    break
        question <= html.DIV(title, **{'class': 'panel-heading'})
        content = html.DIV(**{'class': 'panel-body'})
        question <= content
        summary = html.P()
        description = self.data.get('vt_description') or self.data['summary']
        if description:
            for block in description.split('<br>'):
                if not block.strip():
                    continue
                summary <= block
                summary <= html.BR()
        summary <= html.A('מידע נוסף',
            href='https://oknesset.org/vote/%d/' % self.id)
        content <= summary
        uservote = html.P()
        self.radios = []
        for val, name in self.vals:
            label = html.LABEL()
            btn_div = html.DIV(**{'class': 'btn btn-default'})
            label <= btn_div
            radio = html.INPUT(type='radio', name=str(self.id), value=str(val))
            self.radios.append(radio)
            btn_div <= radio
            btn_div <= ' '+name+' '
            uservote <= label
            uservote <= ' '
        content <= uservote
        self.party_votes_doc = html.P()
        content <= self.party_votes_doc
        if loaded:
            self.load_answer()
        for radio in self.radios:
            radio.bind('change', self.set_answer)

    def load_answer(self):
        key = 'q%d_answer' % self.id
        if key not in storage:
            return
        self.answer = int(storage[key])
        set_radio_val(self.radios, str(self.answer))
        self.calc_party_votes()
        self.show_party_votes()

    def set_answer(self, event):
        first_answer = self.answer is None
        self.answer = int(radio_val(self.radios))
        storage['q%d_answer' % self.id] = str(self.answer)

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
            party = parties[x[0]]
            return (-sum(results.values()), -party['number_of_seats'], -x[0])
        party_votes = self.party_votes
        if game.prev_party not in party_votes:
            party_votes[game.prev_party] = {-1: 0, 1: 0}
        table = html.TABLE(
            style={'text-align': 'center', 'background': '#f9f9f9'},
            **{'class': 'table table-packed'})
        self.party_votes_doc <= html.DIV(table, **{'class': 'table-responsive'})
        parties_row = html.TR(html.TH('מפלגה', style={'vertical-align': 'top'}))
        table <= html.THEAD(parties_row)
        tbody = html.TBODY()
        table <= tbody
        rows = {}
        for (v, name) in self.vals:
            if not v:
                continue
            style = {}
            if self.answer:
                style['background'] = ['#ffdddd', '#ccfacc'][v == self.answer]
            elif not rows:
                style['background'] = 'white'
            row = html.TR(html.TH(name), style=style)
            tbody <= row
            rows[v] = row
        for party_id, results in sorted(party_votes.items(), key=key):
            party = parties[party_id]
            [for_txt, vs_txt] = [
                '%.0f%%'%(100*r/party['number_of_seats']) if r else '-'
                for r in [results[1], results[-1]]]
            for row, val in [
                (parties_row, party.get('short_name') or party['name']),
                (rows[1], for_txt),
                (rows[-1], vs_txt),
                ]:
                if party_id == game.prev_party:
                    val = html.B(val)
                row <= html.TD(val)

    def add_question(self, *args):
        game.add_question()

def is_boring_question(question_data):
    for x in ['for_votes_count', 'against_votes_count']:
        if question_data[x] <= 5:
            return True
    return False

def parse_json(raw_json):
    result = json.loads(raw_json)
    result['raw_json'] = raw_json
    return result

class Game:
    def __init__(self):
        self.questions = []
    def load(self):
        if 'prev_party' not in storage:
            return
        self.prev_party = int(storage['prev_party'])
        set_radio_val(party_radios, str(self.prev_party) if self.prev_party else '')
        if 'questions' in storage:
            for qid in json.loads(storage['questions']):
                question_data = json.loads(storage['q%d_data' % qid])
                question = self.got_question(question_data, loaded=True)
            self.update_results()
            qids = [q.id for q in self.questions]
            questions[:] = [q for q in questions if q['id'] not in qids]
        for q in self.questions:
            if q.answer is None:
                break
        else:
            self.add_question()
    def set_party(self, event):
        prev_party = radio_val(party_radios)
        self.prev_party = int(prev_party) if prev_party else 0
        storage['prev_party'] = str(self.prev_party)
        if self.questions:
            self.update_results()
            for question in self.questions:
                question.show_party_votes()
        else:
            self.add_question()
    def add_question(self):
        if questions:
            self.got_question(questions.pop())
            self.ajax_request_question(self.ajax_response_add_question_to_queue)
        else:
            self.ajax_request_question(self.ajax_response_add_question)
    def ajax_request_question(self, handler):
        req = ajax.ajax()
        req.bind('complete', handler)
        params = ['pp=%d' % self.prev_party]
        for question in self.questions:
            if question.answer is None:
                continue
            params.append('q%d=%d' % (question.id, question.answer))
        req.open('GET', '/get_question/?'+'&'.join(params))
        req.send()
    def ajax_response_add_question(self, req):
        if req.status not in [0, 200]:
            document['debug'].html = req.text
            return
        self.got_question(parse_json(req.text))
    def ajax_response_add_question_to_queue(self, req):
        if req.status not in [0, 200]:
            document['debug'].html = req.text
            return
        question_data = parse_json(req.text)
        if is_boring_question(question_data):
            self.ajax_request_question(self.ajax_response_add_question_to_queue)
            return
        questions.append(question_data)
    def got_question(self, question_data, loaded=False):
        assert question_data['id'] not in [x.id for x in self.questions]
        question = Question(question_data, loaded)
        if not loaded:
            storage['q%d_data' % question.id] = question_data['raw_json']
        self.questions.append(question)
        storage['questions'] = json.dumps([x.id for x in self.questions])
        return question
    def update_results(self):
        results = {}
        num_questions = 0
        for question in self.questions:
            if not question.answer:
                continue
            num_questions += 1
            for party_id, votes in question.party_votes.items():
                party_results = results.setdefault(party_id, {-1: 0, 1: 0})
                for k, v in votes.items():
                    party_results[k * question.answer] += v
        document['results'].clear()
        results_small = document['results-small']
        results_small.clear()
        results_small <= html.B('תוצאות:')
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
        prev_score = None
        for idx, (party_id, score) in enumerate(sorted(list(results.items()), key=key)):
            if idx == 0 or score['overall'] < prev_score['overall']:
                pos = idx+1
            prev_score = score

            if party_id not in parties:
                # party_id is per knesset session at the moment
                # and the oknesset api doesn't give data for old sessions
                # see https://oknesset.org/party/5/ ("ישראל ביתנו בכנסת ה-18")
                continue
            row = html.TR()
            party_name = parties[party_id]['name']
            short_name = '%d. %s' % (pos, parties[party_id].get('short_name') or party_name)
            pos_txt = str(pos)
            if party_id == self.prev_party:
                pos_txt = html.B(pos_txt)
                party_name = html.B(party_name)
                short_name = html.B(short_name)
            results_small <= html.BR()
            results_small <= short_name
            row <= html.TD(pos_txt)
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

def set_radio_val(radios, val):
    for radio in radios:
        if radio.value == val:
            radio.checked = True
            return

party_radios = document['previous_vote'].get(selector='INPUT')
game = Game()
for radio in party_radios:
    radio.bind('change', game.set_party)

game.load()

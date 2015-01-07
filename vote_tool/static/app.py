#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import ajax, document, html, timer

class Question:
    vals = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

    def __init__(self, data):
        self.data = data
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
            href='https://oknesset.org/vote/%d/' % self.data['id'])
        content <= summary
        uservote = html.P()
        self.radios = []
        for val, name in self.vals:
            label = html.LABEL()
            btn_div = html.DIV(**{'class': 'btn btn-default'})
            label <= btn_div
            radio = html.INPUT(type='radio', name=str(self.data['id']), value=str(val))
            radio.bind('change', self.set_answer)
            self.radios.append(radio)
            btn_div <= radio
            btn_div <= ' '+name+' '
            uservote <= label
            uservote <= ' '
        content <= uservote
        self.party_votes_doc = html.P()
        content <= self.party_votes_doc

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
        if questions:
            self.got_question(questions.pop())
            self.ajax_request_question(self.ajax_response_add_question_to_queue)
        else:
            self.ajax_request_question(self.ajax_response_add_question)
    def ajax_request_question(self, handler):
        req = ajax.ajax()
        req.bind('complete', handler)
        params = ['pp=%d' % self.prev_party]
        for question_id, question in self.questions.items():
            if question.answer is None:
                continue
            params.append('q%d=%d' % (question_id, question.answer))
        req.open('GET', '/get_question/?'+'&'.join(params))
        req.send()
    def ajax_response_add_question(self, req):
        if req.status not in [0, 200]:
            document['debug'].html = req.text
            return
        self.got_question(json.loads(req.text))
    def ajax_response_add_question_to_queue(self, req):
        if req.status not in [0, 200]:
            document['debug'].html = req.text
            return
        question_data = json.loads(req.text)
        if is_boring_question(question_data):
            self.ajax_request_question(self.ajax_response_add_question_to_queue)
            return
        questions.append(question_data)
    def got_question(self, question_data):
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

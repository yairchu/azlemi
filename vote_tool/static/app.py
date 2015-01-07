#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import ajax, document, html, timer

answers = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

def render_question_panel(data):
    panel = html.DIV(**{'class': 'panel panel-primary'})
    title = data.get('vt_title')
    if not title:
        title = data['title']
        for prefix in [
            'להעביר את הצעת החוק לוועדה - ',
            'להעביר את הצעת החוק לוועדה שתקבע ועדת הכנסת - ',
            ]:
            if title.startswith(prefix):
                title = title[len(prefix):]
                break
    panel <= html.DIV(title, **{'class': 'panel-heading'})
    content = html.DIV(**{'class': 'panel-body'})
    panel <= content
    summary = html.P()
    description = data.get('vt_description') or data['summary']
    if description:
        for block in description.split('<br>'):
            if not block.strip():
                continue
            summary <= block
            summary <= html.BR()
    summary <= html.A('מידע נוסף',
        href='https://oknesset.org/vote/%d/' % data['id'])
    content <= summary
    uservote = html.P()
    radios = []
    for val, name in answers:
        label = html.LABEL()
        btn_div = html.DIV(**{'class': 'btn btn-default'})
        label <= btn_div
        radio = html.INPUT(type='radio', name=str(data['id']), value=str(val))
        radios.append(radio)
        btn_div <= radio
        btn_div <= ' '+name+' '
        uservote <= label
        uservote <= ' '
    content <= uservote
    party_votes_doc = html.P()
    content <= party_votes_doc
    return panel, party_votes_doc, radios

def render_question_party_votes(party_votes_doc, data, user_answer, highlight_party):
    def key(x):
        results = x[1]
        party = parties[x[0]]
        return (-sum(results.values()), -party['number_of_seats'], -x[0])
    party_votes = data['party_votes'].copy()
    for x in list(party_votes.keys()):
        if x not in parties:
            # Old party not in knesset
            del party_votes[x]
    if highlight_party:
        party_votes.setdefault(highlight_party, {})
    table = html.TABLE(
        style={'text-align': 'center', 'background': '#f9f9f9'},
        **{'class': 'table table-packed'})
    party_votes_doc <= html.DIV(table, **{'class': 'table-responsive'})
    parties_row = html.TR(html.TH('מפלגה', style={'vertical-align': 'top'}))
    table <= html.THEAD(parties_row)
    tbody = html.TBODY()
    table <= tbody
    rows = {}
    for (v, name) in answers:
        if not v:
            continue
        style = {}
        if user_answer:
            style['background'] = ['#ffdddd', '#ccfacc'][v == user_answer]
        elif not rows:
            style['background'] = 'white'
        row = html.TR(html.TH(name), style=style)
        tbody <= row
        rows[v] = row
    for party_id, results in sorted(party_votes.items(), key=key):
        party = parties[party_id]
        [for_txt, vs_txt] = [
            '%.0f%%'%(100*r/party['number_of_seats']) if r else '-'
            for r in [results.get('for'), results.get('against')]]
        for row, val in [
            (parties_row, party.get('short_name') or party['name']),
            (rows[1], for_txt),
            (rows[-1], vs_txt),
            ]:
            if party_id == highlight_party:
                val = html.B(val)
            row <= html.TD(val)

class Question:
    def __init__(self, data):
        self.data = data
        self.answer = None

        panel, self.party_votes_doc, self.radios = render_question_panel(data)
        document['questions'] <= panel
        for radio in self.radios:
            radio.bind('change', self.set_answer)

    def set_answer(self, event):
        first_answer = self.answer is None
        self.answer = int(radio_val(self.radios))
        self.show_party_votes()
        game.update_results()
        if first_answer:
            timer.request_animation_frame(self.add_question)

    def show_party_votes(self):
        self.party_votes_doc.clear()
        if self.answer is None:
            return
        render_question_party_votes(self.party_votes_doc, self.data, self.answer, game.prev_party)

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
    def set_party(self, event = None):
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
            for party_id, votes in question.data['party_votes'].items():
                if party_id not in parties:
                    continue
                party_results = results.setdefault(party_id, {-1: 0, 1: 0})
                for k, v in votes.items():
                    pval = {'for': 1, 'against': -1}[k]
                    party_results[pval * question.answer] += v
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

game = Game()

party_of_member = dict((x['id'], x['party_id']) for x in members)

party_radios = document['previous_vote'].get(selector='INPUT')
for radio in party_radios:
    radio.bind('change', game.set_party)
    if radio.checked:
        game.set_party()

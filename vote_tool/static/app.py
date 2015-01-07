#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import ajax, document, html, timer

import render_content

party_of_member = dict((x['id'], x['party_id']) for x in members)

class Question:
    def __init__(self, data):
        self.data = data

    def render(self):
        panel, _, _ = render_content.question_panel(self.data)
        document['questions'] <= panel
        self.bind_buttons()

    def bind_buttons(self):
        key = 'q%d'%self.data['id']
        val = radio_val(key)
        self.answer = int(val) if val is not None else None
        for radio in radios_of(key):
            radio.bind('change', self.set_answer)

    def set_answer(self, event):
        first_answer = self.answer is None
        self.answer = int(radio_val('q%d'%self.data['id']))
        self.show_party_votes()
        game.update_results()
        timer.request_animation_frame(game.add_question if first_answer else game.save_vote)

    def show_party_votes(self):
        party_votes_doc = document['q%d_party_votes'%self.data['id']]
        party_votes_doc.clear()
        if self.answer is None:
            return
        render_content.question_party_votes(party_votes_doc, self.data, self.answer, game.prev_party, parties)

def is_boring_question(question_data):
    for x in ['for_votes_count', 'against_votes_count']:
        if question_data[x] <= 5:
            return True
    return False

class Game:
    def __init__(self):
        self.questions = {}
        self.prev_party = 0
    def set_party(self, event = None):
        prev_party = radio_val('previous_vote')
        self.prev_party = int(prev_party) if prev_party else 0
        if self.questions and event is not None:
            self.update_results()
            for question in self.questions.values():
                question.show_party_votes()
        for question in self.questions.values():
            if question.answer is not None:
                if event is not None:
                    self.save_vote()
                break
        else:
            self.add_question()
    def add_question(self, *args):
        if questions:
            self.got_question(questions.pop())
            self.ajax_request_question(self.ajax_response_add_question_to_queue)
        else:
            self.ajax_request_question(self.ajax_response_add_question)
    def save_vote_query(self):
        params = ['pp=%d' % self.prev_party]
        for question_id, question in self.questions.items():
            if question.answer is None:
                continue
            params.append('q%d=%d' % (question_id, question.answer))
        return '&'.join(params)
    def save_vote(self, *args):
        req = ajax.ajax()
        req.open('GET', '/save_vote/?'+self.save_vote_query())
        req.send()
    def ajax_request_question(self, handler):
        req = ajax.ajax()
        req.bind('complete', handler)
        req.open('GET', '/get_question/?'+self.save_vote_query())
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

    def got_question(self, question_data, render=True):
        question_id = question_data['id']
        assert question_id not in self.questions
        question = Question(question_data)
        if render:
            question.render()
        else:
            question.bind_buttons()
        self.questions[question_id] = question

    def update_results(self):
        results = render_content.calc_results(
            dict((k, v.data) for k, v in self.questions.items()),
            dict((k, v.answer) for k, v in self.questions.items()
                if v.answer is not None),
            parties,
            )

        document['results'].clear()
        document['results-small'].clear()
        results_small = render_content.render_results(document['results'], document['results-small'], results, self.prev_party, parties)

def id_from_uri(uri):
    return int(uri.rstrip('/').rsplit('/', 1)[1])

def radios_of(elem_id):
    return document[elem_id].get(selector='INPUT')

def radio_val(elem_id):
    for radio in radios_of(elem_id):
        if radio.checked:
            return radio.value

game = Game()

for question in prev_questions:
    game.got_question(question, False)
for question in game.questions.values():
    if question.answer is None:
        break
else:
    timer.request_animation_frame(game.add_question)

for radio in radios_of('previous_vote'):
    radio.bind('change', game.set_party)
    if radio.checked:
        game.set_party()

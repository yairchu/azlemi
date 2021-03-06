#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from browser import ajax, document, html, timer, window

def translate(text):
    return window.client_side_translations.get(text, text)

class Question:
    def __init__(self, data):
        self.data = data

    def render(self):
        panel, _, _ = window.render_content['question_panel'](self.data, window.is_staff, translate)
        document['questions'] <= panel

        dollar = getattr(window, '$')

        desc_id = 'q%d-desc' % self.data['id']
        for desc in panel.get(selector='p[data-toggle]'):
            desc.id = desc_id
        dollar('#'+desc_id).tooltip()

        box_id = 'q%d' % self.data['id']
        try:
            dollar('#'+box_id).jTinder(window.jTinderConfig)
        except AttributeError:
            pass

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
        window.render_content['question_party_votes'](party_votes_doc, self.data, self.answer, translate)

def is_boring_question(question_data):
    for x in ['for_votes_count', 'against_votes_count']:
        if question_data[x] <= 5:
            return True
    return False

class Game:
    def __init__(self):
        self.hide_previous_questions = False
        self.finish_after_enough_answers = False

        self.questions = []
        self.congrats_panel_shown = False
    def congrat(self):
        if self.congrats_panel_shown:
            return
        self.congrats_panel_shown = True
        _ = translate
        panel = html.DIV(style={'text-align': 'center'})
        panel <= html.BR()
        panel <= html.SPAN(
            _(window.texts['congrat']) % window.num_questions_to_answer,
            style={'font-size': '20px'})
        panel <= html.BR()
        panel <= html.BR()
        panel <= html.A(
            _(window.texts['congrat_results']), href='#results',
            Class='btn btn-lg btn-success')
        panel <= html.BR()
        panel <= html.BR()
        panel <= _(window.texts['congrat_resume'])
        panel <= html.BR()
        panel <= html.BR()
        document['questions'] <= panel
    def add_question(self, *args):
        num_answered = len([x for x in self.questions if x.answer])
        if num_answered == window.num_questions_to_answer:
            if self.finish_after_enough_answers:
                return
            self.congrat()
        if window.questions:
            self.got_question(window.questions.pop())
            if len(window.questions) < 3:
                self.ajax_request_question(self.ajax_response_add_question_to_queue)
        else:
            self.ajax_request_question(self.ajax_response_add_question)
    def save_vote_query(self):
        params = []
        for question in self.questions:
            if question.answer is None:
                continue
            params.append('q%d:%d' % (question.data['id'], question.answer))
        if not params:
            return {}
        return {'s': ','.join(params)}
    def save_vote(self, *args):
        req = ajax.ajax()
        req.open('GET',
            window.root_url +
            '/save_vote/?' + self.save_vote_query() +
            '&callback=?')
        req.send()
    def ajax_request_question(self, handler):
        req = ajax.ajax()
        req.bind('complete', handler)
        queue = [q['id'] for q in window.questions]
        for question in self.questions:
            if question.answer is None:
                queue.append(question.data['id'])
        params = self.save_vote_query()
        params['queue'] = ','.join('q%d'%x for x in queue)
        req.open('GET',
            window.root_url +
            translate('/') + 'get_question/?' +
            '&'.join('%s=%s'%(k, v) for k, v in params.items()) +
            '&callback=?')
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
        window.questions.append(question_data)

    def got_question(self, question_data, render=True):
        question_id = question_data['id']
        for question in self.questions:
            assert question_id != question.data['id']
        question = Question(question_data)
        if self.hide_previous_questions:
            document['questions'].clear()
        if render:
            question.render()
        else:
            question.bind_buttons()
        self.questions.append(question)

    def update_results(self):
        user_answers = dict(
            (q.data['id'], q.answer) for q in self.questions
            if q.answer is not None)
        results = window.render_content['calc_results'](
            dict((q.data['id'], q.data) for q in self.questions), user_answers)

        parts = {}
        for k in ['results', 'results-small', 'radial-progress-bar', 'progress-bar']:
            try:
                parts[k] = document[k]
            except KeyError:
                parts[k] = html.DIV()
            else:
                parts[k].clear()
        window.render_content['render_results'](
            parts['results'], parts['results-small'],
            parts['progress-bar'], parts['radial-progress-bar'],
            results, user_answers, translate)

    def start(self):
        for question in self.questions:
            if question.answer is None:
                break
        else:
            timer.request_animation_frame(self.add_question)

def id_from_uri(uri):
    return int(uri.rstrip('/').rsplit('/', 1)[1])

def radios_of(elem_id):
    return document[elem_id].get(selector='INPUT')

def radio_val(elem_id):
    for radio in radios_of(elem_id):
        if radio.checked:
            return radio.value

game = Game()

for question in window.prev_questions:
    game.got_question(question, False)

window.game = game

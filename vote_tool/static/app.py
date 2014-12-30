#!/usr/bin/python3
# -*- coding: utf8 -*-

import json

from browser import document, html

class Question:
    vals = list(zip([-1, 0, 1], ['כן', 'אולי', 'לא']))

    def __init__(self, data):
        self.data = data
        self.answer = None

        header = html.H4()
        header <= self.data['title']
        document['questions'] <= header
        self.radios = []
        for _, name in self.vals:
            radio = html.INPUT(type='radio', name=str(self.data['id']))
            radio.bind('change', self.set_answer)
            self.radios.append(radio)
            document['questions'] <= radio
            document['questions'] <= name

    def set_answer(self, event):
        first_answer = self.answer is None
        for i, radio in enumerate(self.radios):
            if radio.checked:
                val, _ = self.vals[i]
                break
        self.answer = val

        game.update_results()
        if first_answer:
            game.add_question()

class Game:
    def __init__(self):
        self.questions = {}
    def start(self, event):
        if self.questions:
            # already started
            return
        self.add_question()
    def add_question(self):
        # Get new question (not already asked)
        while True:
            question_data = json.loads(open('/get_question/').read())
            question_id = question_data['id']
            if question_id not in self.questions:
                break
        question = Question(question_data)
        self.questions[question_id] = question
    def update_results(self):
        results = {}
        for question in self.questions.values():
            if not question.answer:
                continue
            for vote in question.data['votes']:
                if 'for' == vote['vote_type']:
                    val = 1
                elif 'against' == vote['vote_type']:
                    val = -1
                else:
                    continue
                party_id = party_of_member[id_from_uri(vote['member'])]
                score = val * question.answer
                results[party_id] = score + results.get(party_id, 0)

        table = html.TABLE()
        row = html.TR()
        row <= html.TH('מפלגה') <= html.th('ניקוד')
        table <= row
        def key(x):
            return x[1]
        for party_id, score in sorted(list(results.items()), key=key):
            if party_id not in parties:
                # party_id is per knesset session at the moment
                # and the oknesset api doesn't give data for old sessions
                # see https://oknesset.org/party/5/ ("ישראל ביתנו בכנסת ה-18")
                continue
            row = html.TR()
            row <= html.TD(parties[party_id]['name'])
            row <= html.TD(str(score))
            table <= row
        document['results'].clear()
        document['results'] <= html.H3('תוצאות:')
        document['results'] <= table

def id_from_uri(uri):
    return int(uri.rstrip('/').rsplit('/', 1)[1])

game = Game()

parties = json.loads(open('oknesset/api/v2/party').read())['objects']
parties = dict((x['id'], x) for x in parties)

members = json.loads(open('data/member_info.json').read())
party_of_member = dict((x['id'], x['party_id']) for x in members)

def party_entry(val, name):
    radio = html.INPUT(type='radio', name='previous_vote', value=val)
    radio.bind('change', game.start)
    document['previous_vote'] <= radio
    document['previous_vote'] <= name

parties_list = html.UL()
party_entry('', 'לא הצבעתי')
for party in parties.values():
    party_entry(party['id'], party['name'])

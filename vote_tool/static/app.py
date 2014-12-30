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

game = Game()

parties = json.loads(open('oknesset/api/v2/party').read())['objects']

def party_entry(val, name):
    radio = html.INPUT(type='radio', name='previous_vote', value=val)
    radio.bind('change', game.start)
    document['previous_vote'] <= radio
    document['previous_vote'] <= name

parties_list = html.UL()
party_entry('', 'לא הצבעתי')
for party in parties:
    party_entry(party['id'], party['name'])

'''
This script helps me find interesting votes based on the "wisdom of the crowd".

azlemi.org.il was initially seeded with votes I picked from open knesset's
site (oknesset.org/vote) trying different filterings (most controversial, etc).
The site used these more interesting votes with a random pick of totally random
votes too, to obtain this crowd-data.
Now based on crowd data (of approx 20000 users as of 2015.2.2)
I can see which questions tend to be skipped, and which have more varied
user answers (more dilemma is probably more interesting).

This is feeded from csvs exported from heroku dataclips:

https://dataclips-next.heroku.com/lnmhtrnoctzpsubnciuxkjwbbgdl-azlemiorg-list-of-votes
export to votes.csv

https://dataclips-next.heroku.com/ujtrqptepdhwowqujfdwkcbhahwz-azlemiorg-vote-answers-statistics
export to answers.csv
'''

import csv
import pprint
import sys

data = {}
for row in csv.DictReader(open('votes.csv')):
    data[int(row['id'])] = {
        'answers': {-1: 0, 0: 0, 1: 0},
        'is_interesting': row['is_interesting'].lower() == 'true',
        'title': row['title'],
        }

for row in csv.DictReader(open('answers.csv')):
    data[int(row['vote_id'])]['answers'][int(row['answer'])] = int(row['count'])

def key(item):
    k, v = item
    answers = v['answers']
    d = sum(answers.values())+1
    return d < 10, (answers[0] + max(answers[1], answers[-1])) / d

def is_simple(item):
    k, v = item
    return 'הסתייגות' not in v['title']

for i, item in enumerate(sorted(filter(is_simple, data.items()), key=key)):
    if i == 20:
        break
    vote_id, data = item
    a = data['answers']
    print(data['title'])
    print('%s %5d. %3d %3d %3d' % (
        ' V'[data['is_interesting']], vote_id, a[-1], a[0], a[1]))
    print()

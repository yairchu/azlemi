from django.core.management.base import BaseCommand

from vote import models, views, render_content

class Command(BaseCommand):
    help = '''
    Find votes to separate a party pair

    vote_for_party_pair <party-a> <party-b> <candidate-vote-ids>

    candidate-vote-ids should be comma separated list, like that out of
    "interesting_questions_list.py --list
    '''

    def handle(self, *args, **options):
        [party_a, party_b, votes_str] = args
        party_a = party_a.replace('_', ' ')
        party_b = party_b.replace('_', ' ')
        vote_ids = [int(x) for x in votes_str.split(',')]
        votes = []
        def party_score(party):
            party_votes = vote['party_votes'][party]
            return party_votes.get('for', 0) - party_votes.get('against', 0)
        for vote in models.Vote.objects.filter(id__in=tuple(vote_ids)):
            vote = views.export_vote(vote)
            score_a = party_score(party_a)
            score_b = party_score(party_b)
            vote['score'] = (score_a * score_b < 0) + abs(score_a - score_b)
            votes.append(vote)
        def key(vote):
            return -vote['score']
        for vote in sorted(votes, key=key)[:10]:
            print(vote['title'])
            print('%5d. %3d %3d %3.0f%% %3.0f%%' % (
                vote['id'],
                vote['for_votes_count'], vote['against_votes_count'],
                party_score(party_a) * 100, party_score(party_b) * 100))
            print()

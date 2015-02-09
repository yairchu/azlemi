from django.core.management.base import BaseCommand

from vote import models, views, render_content

class Command(BaseCommand):
    help = '''
    Find pairs of parties that tend to be at first and second place together.
    Based on users' shared results / "wisdom of the crowd".
    '''

    def handle(self, *args, **options):
        count_of_pair = {}
        for publish in models.Publish.objects.all():
            user_answers, vote_ids = views.parse_publish_votes_str(
                publish.votes)
            votes = {}
            for vote in models.Vote.objects.filter(id__in=tuple(vote_ids)):
                vote = views.export_vote(vote)
                votes[vote['id']] = vote
            (results, _unused) = render_content.calc_results(
                votes, user_answers)
            top_two_parties = tuple(sorted(
                party_name for pos, party_name, score in
                list(render_content.sorted_results(results))[:2]))
            count_of_pair[top_two_parties] = 1 + count_of_pair.get(
                top_two_parties, 0)
        def key(item):
            key, val = item
            return -val

        for (a, b), count in sorted(count_of_pair.items(), key=key)[:50]:
            print('%s vs %s: %d' % (a, b, count))

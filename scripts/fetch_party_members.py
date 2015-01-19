'''
Open Knesset's API does not provide the data for
membership in parties of the 18th Knesset, but only the current knesset.

This script fetches the site's user-facing pages to obtain this data.
'''

import json
import itertools
import urllib.request

members_of_party = {}

def get_page_with_retries(url, num_retries=3):
    for attempt in range(num_retries-1):
        try:
            return urllib.request.urlopen(url).read()
        except:
            pass
    return urllib.request.urlopen(url).read()

for party_id in itertools.count(1):
    url = 'https://oknesset.org/party/%d/' % party_id
    try:
        page_content = get_page_with_retries(url).decode('utf8')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            break
    parts = page_content.split('<div class="party-member-photo">')[1:]
    members = []
    for part in parts:
        members.append(int(part.split('<a href="/member/')[1].split('/')[0]))
    print('party %d members: %s' % (party_id, members))
    members_of_party[party_id] = members

# Shas override:
# In the 19th Knesset a bunch of MPs quit at the very end of the knesset
# and Open Knesset's data represents the party after the event even though
# it makes more sense to look at it before that.

member_json = json.load(open('vote/data/oknesset/api/v2/member/_limit=0'))
member_id_of_name = {}
for member_data in member_json['objects']:
    member_id_of_name[member_data['name']] = member_data['id']

shas_knesset_19_id = 18 # https://oknesset.org/party/18/
members_of_party[shas_knesset_19_id] = [
    member_id_of_name[member_name]
    for member_name in [
        'אליהו ישי',
        'אריה דרעי',
        'אריאל אטיאס',
        'יצחק כהן',
        'משולם נהרי',
        'אמנון כהן',
        'יעקב מרגי',
        'דוד אזולאי',
        'יצחק וקנין',
        'נסים זאב',
        'אברהם מיכאלי',
        ]
    ]

open('members_of_party.json','w').write(json.dumps(members_of_party, ensure_ascii=False))

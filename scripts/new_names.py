'''
Helper script to find wrong/inconsistent spellings in knesset_20_parties.json
'''

import json

def decomment(txt):
    parts = txt.split('/*')
    return ''.join(parts[:1] + [x.split('*/', 1)[1] for x in parts[1:]])

old_members = json.load(open('vote/data/oknesset/api/v2/member/_limit=0'))
new_members = json.loads(decomment(
    open('scripts/data/knesset_20_parties.json').read()))

old_member_names = set(x['name'] for x in old_members['objects'])
for party_name, members in new_members.items():
    if not isinstance(members, list):
        continue
    print()
    print(party_name)
    for i, name in enumerate(members):
        if name in old_member_names:
            continue
        print('  %d. %s' % (i+1, name))

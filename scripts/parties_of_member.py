import json

def decomment(txt):
    parts = txt.split('/*')
    return ''.join(parts[:1] + [x.split('*/', 1)[1] for x in parts[1:]])

knesset_20 = json.loads(
    decomment(open('scripts/data/knesset_20_parties.json','rb'
        ).read().decode('utf8')))
members_of_past_parties = json.load(open('vote/data/members_of_party.json'))
past_parties = json.load(open('vote/data/oknesset/api/v2/party/_knesset=all'))
past_members = json.load(open('vote/data/oknesset/api/v2/member/_limit=0'))

def normalize_unicode(text):
    # this fixes party names so that names from 19th knesset and 18th match
    # ie ש”ס vs ש"ס
    return text.replace('"', '”').strip()

party_long_and_short_names = [
  ('חזית דמוקרטית לשלום ושוויון', 'חד”ש'),
  ('ברית לאומית דמוקרטית', 'בל”ד'),
  ]

past_parties = past_parties['objects']
for p in past_parties:
    p['name'] = normalize_unicode(p['name'])
    for long_name, short_name in party_long_and_short_names:
        if p['name'] == short_name:
            p['name'] = long_name
        if p['name'] == long_name:
            p['short_name'] = short_name
past_party_of_id = dict((x['id'], x) for x in past_parties)

past_member_of_id = dict((x['id'], x) for x in past_members['objects'])

member_names = set()
for name_list in knesset_20.values():
    if not isinstance(name_list, list):
        continue
    for name in name_list:
        member_names.add(name)
for member in past_members['objects']:
    member_names.add(member['name'])

party_of_member = {}
for party_id_str, members in members_of_past_parties.items():
    party = past_party_of_id[int(party_id_str)]
    party_name = party['name']
    if party_name in knesset_20:
        knesset_20_data = knesset_20[party_name]
        if knesset_20_data is None:
            continue
        if isinstance(knesset_20_data, str):
            party_name = knesset_20_data
    knesset_id = party['knesset_id']
    for member_id in members:
        member = past_member_of_id[member_id]
        name = member['name']
        party_of_member.setdefault(name, {})[knesset_id] = party_name
for party_name, member_names in knesset_20.items():
    if not isinstance(member_names, list):
        continue
    for name in member_names:
        if name not in party_of_member:
            # We don't need data for members who were never in the knesset
            continue
        party_of_member[name][20] = party_name

print(json.dumps(party_of_member, ensure_ascii=False))

import json

next_knesset = 20
parties_of_member = json.load(open('vote/data/parties_of_member.json'))

result = {}

for party_per_knesset in parties_of_member.values():
    party_in_next = party_per_knesset.get(str(next_knesset))
    for knesset_id_str, party_in_that in party_per_knesset.items():
        knesset_id = int(knesset_id_str)
        if knesset_id == next_knesset:
            continue
        for party in [party_in_that, party_in_next]:
            if party is None:
                continue
            party_res = result.setdefault(party, {})
            party_res[knesset_id] = 1 + party_res.get(knesset_id, 0)

print(json.dumps(result, ensure_ascii=False))

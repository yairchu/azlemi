'''
Generate list of new parties that had any MP in a Knesset.
'''

import json

parties_of_member = json.load(open('vote/data/parties_of_member.json'))

result = {}
for member_parties in parties_of_member.values():
    for k, v in member_parties.items():
        k = int(k)
        if k == 20:
            continue
        result.setdefault(k, set()).add(v)
        if '20' in member_parties:
            result[k].add(member_parties['20'])
for k in result:
    result[k] = sorted(list(result[k]))

print(json.dumps(result, ensure_ascii=False, sort_keys=True))

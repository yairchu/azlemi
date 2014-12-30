import json
import os
import urllib.request

dirname = os.path.dirname(os.path.abspath(__file__))
oknesset_path = dirname+'/../vote_tool/static/oknesset'
members = json.load(open(oknesset_path+'/api/v2/member/_limit=0'))['objects']

result = []
for member in members:
    for attempts in range(10):
        print('getting data for %d' % member['id'])
        try:
            member = json.loads(urllib.request.urlopen(
                'https://oknesset.org/api/v2/member/%d/' % member['id']
                ).read().decode('utf8'))
        except Exception as e:
            exception = e
        else:
            break
    else:
        raise exception
    result.append({
        'id': member['id'],
        'party_id': int(member['party_url'].rstrip('/').rsplit('/',1)[1]),
        })
print('results:\n')
print(json.dumps(result))

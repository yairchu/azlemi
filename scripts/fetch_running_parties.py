'''
Fetch running parties from bechirot.gov.il (the Israeli elections committee)
'''

import json
import urllib.request

from bs4 import BeautifulSoup

root_url = 'http://bechirot.gov.il/election/Candidates/Pages/default.aspx'
root_url_dir = root_url.rsplit('/', 1)[0]
root_page = BeautifulSoup(urllib.request.urlopen(root_url).read())

results = {}

for party_element in root_page.find_all(**{'class': 'linkKnessetTitle'}):
    link_element = party_element.find('a')
    party_name = link_element.string
    print(party_name)
    party_rel_url = link_element['href']
    party_abs_url = root_url_dir + '/' + party_rel_url
    party_page = BeautifulSoup(urllib.request.urlopen(party_abs_url).read())
    members = []
    for candidate_element in party_page.find_all(**{'class': 'candidate'}):
        member_name_last_first = candidate_element.string
        member_name_parts = member_name_last_first.split()
        member_name = ' '.join(member_name_parts[1:] + member_name_parts[:1])
        members.append(member_name)
    results[party_name] = members

open('running_parties.json','w').write(json.dumps(results, ensure_ascii=False, sort_keys=True))

import json

from browser import document, html

members = json.loads(open('oknesset/api/v2/member/_limit=0').read())['objects']

table = html.TABLE()
for member in members:
    row = html.TR()
    row <= member['name']
    table <= row
document <= table

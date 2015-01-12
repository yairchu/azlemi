from browser import html

answers = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

def question_panel(data):
    panel = html.DIV(id='q%d'%data['id'], **{'class': 'panel panel-primary'})
    title = data.get('vt_title')
    if not title:
        title = data['title']
        for prefix in [
            'להעביר את הצעת החוק לוועדה - ',
            'להעביר את הצעת החוק לוועדה שתקבע ועדת הכנסת - ',
            ]:
            if title.startswith(prefix):
                title = title[len(prefix):]
                break
    panel <= html.DIV(title, **{'class': 'panel-heading'})
    content = html.DIV(**{'class': 'panel-body'})
    panel <= content
    description = data.get('vt_description') or data['summary']
    summary = html.P()
    if description:
        too_long = 300
        if len(description) > too_long:
            summary = html.P(
                tooltip=description.replace('<br>', ' '),
                **{'class': 'has-tooltip'})
            description = description[:too_long-3]+'...'
        for block in description.split('<br>'):
            if not block.strip():
                continue
            summary <= block
            summary <= html.BR()
    summary <= html.A(
        'מידע נוסף',
        target='_blank',
        href='https://oknesset.org/vote/%d/' % data['id'],
        )
    content <= summary
    radios = []
    for val, name in answers:
        label = html.LABEL()
        content <= label
        btn_div = html.DIV(**{'class': 'btn btn-default'})
        label <= btn_div
        radio = html.INPUT(type='radio', name=str(data['id']), value=str(val))
        radios.append(radio)
        btn_div <= radio
        btn_div <= ' '+name+' '
        content <= ' '
    party_votes_doc = html.DIV(id='q%d_party_votes'%data['id'])
    content <= party_votes_doc
    return panel, party_votes_doc, radios

def question_party_votes(party_votes_doc, data, user_answer, highlight_party, parties):
    def key(x):
        results = x[1]
        party = parties[x[0]]
        return (-sum(results.values()), -party['number_of_seats'], -x[0])
    party_votes = dict((int(k), v) for k, v in data['party_votes'].items())
    for x in list(party_votes.keys()):
        if x not in parties:
            # Old party not in knesset
            del party_votes[x]
    if highlight_party:
        party_votes.setdefault(highlight_party, {})
    table = html.TABLE(
        style={'text-align': 'center', 'background': '#f9f9f9'},
        **{'class': 'table table-packed'})
    party_votes_doc <= html.DIV(table, **{'class': 'table-responsive'})
    parties_row = html.TR(html.TH('מפלגה', style={'vertical-align': 'top'}))
    table <= html.THEAD(parties_row)
    tbody = html.TBODY()
    table <= tbody
    rows = {}
    for (v, name) in answers:
        if not v:
            continue
        style = {}
        if user_answer:
            style['background'] = ['#ffdddd', '#ccfacc'][v == user_answer]
        elif not rows:
            style['background'] = 'white'
        row = html.TR(html.TH(name), style=style)
        tbody <= row
        rows[v] = row
    for party_id, results in sorted(party_votes.items(), key=key):
        party = parties[party_id]
        [for_txt, vs_txt] = [
            '%.0f%%'%(100*r/party['number_of_seats']) if r else '-'
            for r in [results.get('for'), results.get('against')]]
        for row, val in [
            (parties_row, party.get('short_name') or party['name']),
            (rows[1], for_txt),
            (rows[-1], vs_txt),
            ]:
            if party_id == highlight_party:
                val = html.B(val)
            row <= html.TD(val)

def calc_results(questions, user_answers, parties):
    results = {}
    num_questions = 0
    for qid, answer in user_answers.items():
        if not answer:
            continue
        num_questions += 1
        question = questions[qid]
        for party_id, votes in question['party_votes'].items():
            party_id = int(party_id)
            if party_id not in parties:
                continue
            party_results = results.setdefault(party_id, {-1: 0, 1: 0})
            for k, v in votes.items():
                v = int(v)
                vote_vals = {'for': 1, 'against': -1}
                if k not in vote_vals:
                    continue
                party_results[vote_vals[k] * answer] += v
    for party_id, s in results.items():
        s['overall'] = s[1] - s[-1]
        max_count = parties[party_id]['number_of_seats'] * num_questions
        for k in s.keys():
            s[k] /= max_count
    return results

def render_results(results_dest, results_small, results, highlight_party, parties):
    if not results:
        results_dest <= html.TR(html.TD('תענה על שאלות כדי לקבל תוצאות..', colspan=5))
        return

    results_small <= html.B('תוצאות:')

    def key(x):
        return (-x[1]['overall'], x[0])
    prev_score = None
    for idx, (party_id, score) in enumerate(sorted(list(results.items()), key=key)):
        if idx == 0 or score['overall'] < prev_score['overall']:
            pos = idx+1
        prev_score = score

        if party_id not in parties:
            # party_id is per knesset session at the moment
            # and the oknesset api doesn't give data for old sessions
            # see https://oknesset.org/party/5/ ("ישראל ביתנו בכנסת ה-18")
            continue
        row = html.TR()
        party_name = parties[party_id]['name']
        short_name = '%d. %s' % (pos, parties[party_id].get('short_name') or party_name)
        pos_txt = str(pos)
        if party_id == highlight_party:
            pos_txt = html.B(pos_txt)
            party_name = html.B(party_name)
            short_name = html.B(short_name)
        results_small <= html.BR()
        results_small <= short_name
        row <= html.TD(pos_txt)
        row <= html.TD(party_name)
        for k in [1, -1, 'overall']:
            cell = '%.0f%%'%(100*score[k])
            if party_id == highlight_party:
                cell = html.B(cell)
            row <= html.TD(cell, dir='ltr')
        results_dest <= row
